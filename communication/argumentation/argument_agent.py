"""Argument agent"""
# pylint: disable=W0631
from copy import deepcopy
from functools import reduce
from typing import Dict, List, Optional

from communication.agent.communicating_agent import CommunicatingAgent
from communication.argumentation.states import NegotationState
from communication.arguments.argument import Argument
from communication.arguments.comparison import Comparison
from communication.arguments.couple_value import CoupleValue
from communication.message.message import Message
from communication.message.message_performative import MessagePerformative
from communication.preferences import CriterionName, Item, Preferences, Value


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent ."""

    def __init__(
        self, unique_id, model, name: str, items: List[Item], preferences: Preferences
    ):
        super().__init__(unique_id, model, name)
        self.__preferences = preferences
        self.items = sorted(
            items,
            key=lambda item: item.get_score(self.__preferences),  # type: ignore
            reverse=True,
        )
        self.proposed_items = []
        self.negotation_state = NegotationState.REST
        # self.current_item = self.items[0]
        self.current_item: Optional[str] = None
        self.convinced_agents: Dict[str, bool] = {}
        self.other_agent_views = {}
        self.arguments_used = []
        # self.item_was_proposed = False

    def __str__(self) -> str:
        return f"""
        Secret presentation (only you are seeing it):
        ---------------------------------------------
        My name is Agent {self.name}
        My favorite item is {self.items[0]} with score {self.items[0].get_score(self.__preferences)}
        """

    @property
    def preferences(self) -> Preferences:
        """Get preferences"""
        return self.__preferences

    def step(self):
        """Step function"""

        # First step: we must begin the conversation
        if self.negotation_state == NegotationState.REST:
            self.__start_conversation()

        for new_message in self.get_new_messages():

            if new_message.performative == MessagePerformative.PROPOSE:
                self.__propose_performative_callback(new_message)

            # Second case: the other agent sends an accept message
            elif new_message.performative == MessagePerformative.ACCEPT:
                self.__accept_performative_callback(new_message)

            # Third case: the other agent sends an ask why message
            elif new_message.performative == MessagePerformative.ASK_WHY:
                self.__ask_why_performative_callback(new_message)

            # Fourth case: the other agent sends an argue why message
            elif new_message.performative == MessagePerformative.ARGUE:
                self.__add_view_to_history(new_message)
                self.__argue_performative_callback(new_message)

            # Fifth case: the other agent sends a commit message
            elif new_message.performative == MessagePerformative.COMMIT:
                self.__commit_performative_callback(new_message)

    def attack_argument(
        self,
        premises_comparison: List[Comparison],
        premises_couple_value: List[CoupleValue],
        item: Item,
        is_chosen: bool,
    ):
        """Attack argument"""

        def argue_criterion_is_bad(arg: Optional[Argument]):
            """Argue criterion is bad"""
            if arg is None:
                arg = Argument(not is_chosen, item)

            arg.add_premiss_couple_values(
                CoupleValue(
                    premise.criterion_name,
                    self.__preferences.get_value(item, premise.criterion_name),
                )
            )

            if not self.__argument_was_used(arg):
                return arg
            return None

        def argue_found_better_item_for_criterion(arg: Optional[Argument]):
            """Arguments for found better item for a criterion"""
            print("Not implemented")
            return arg

        def argue_found_other_more_important_criterion_is_bad(
            arg: Optional[Argument], bad_criterion: CriterionName
        ):
            """Arguments for found other more important criterion"""
            if arg is None:
                arg = Argument(not is_chosen, item)

            arg.add_premiss_couple_values(
                CoupleValue(
                    bad_criterion, self.__preferences.get_value(item, bad_criterion)
                )
            )

            arg.add_premiss_comparison(
                Comparison(bad_criterion, premise.criterion_name)
            )

            if not self.__argument_was_used(arg):
                return arg
            return None

        counter_argument: Optional[Argument] = None

        for premise in premises_couple_value:  # couple criterion value

            if is_chosen:
                # Another more important criterion is bad
                bad_criterion = self.other_more_important_criterion_is_bad(
                    premise, item
                )
                if bad_criterion is not None:
                    counter_argument = (
                        argue_found_other_more_important_criterion_is_bad(
                            counter_argument, bad_criterion
                        )
                    )

                # For me, the evaluated criterion is bad
                if counter_argument is not None and self.criterion_is_bad(
                    premise, item
                ):
                    counter_argument = argue_criterion_is_bad(counter_argument)

                # I prefer another item which is better for this criterion
                if (
                    counter_argument is not None
                    and self.found_better_item_for_criterion(premise, item)
                ):
                    counter_argument = argue_found_better_item_for_criterion(
                        counter_argument
                    )

                if counter_argument is not None:
                    return counter_argument

                return None

            else:
                other_item_better_on_crietrion = self.other_item_better_on_criterion(
                    premise=premise, item=item
                )

                if other_item_better_on_crietrion is not None:

                    return argue_found_other_more_important_criterion_is_bad(
                        counter_argument, other_item_better_on_crietrion
                    )

                return None

    def get_best_item_to_propose(self) -> Optional[Item]:
        """Get best item to propose"""
        for item in self.items:
            if (
                item.name not in self.proposed_items
            ):  # and self.preferences.is_item_among_top_10_percent():
                self.proposed_items.append(item.name)
                return item

    def __add_view_to_history(self, new_message: Message) -> None:
        """Add view to history"""
        if new_message.sender not in self.other_agent_views:
            self.other_agent_views[new_message.sender] = deepcopy(self.preferences)
        if isinstance(new_message.content, Argument):
            argument = new_message.content
            preferences = self.other_agent_views[new_message.sender]
            for comparison in argument.premises_comparison:
                preferences.set_criterion_pair(
                    comparison.worst_criterion_name, comparison.best_criterion_name
                )

            for couple_value in argument.premises_couple_values:
                preferences.set_criterion_value(
                    argument.item, couple_value.criterion_name, couple_value.value
                )

    def __propose_new_item(self) -> None:
        """Propose new item"""
        self.convinced_agents = {}
        for agent in self.model.schedule.agents:
            if agent.name != self.name:
                self.__send_propose_message(agent.name)
        self.negotation_state = NegotationState.ARGUING

    def __start_conversation(self):
        """Start conversation"""
        min_id = self.unique_id
        for agent in self.model.schedule.agents:
            min_id = min(min_id, agent.unique_id)

        # Agent with min id starts the conversation
        if min_id == self.unique_id:
            self.current_item = self.get_best_item_to_propose()
            self.__propose_new_item()

    def __commit_performative_callback(self, message: Message) -> None:
        """Commit performative callback: the other agent commits an item."""

        if (
            self.current_item.name == message.content.name
            and self.current_item.name in [item.name for item in self.items]
        ):
            if self.negotation_state == NegotationState.WAITING_ANSWER_ACCEPT:
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.COMMIT,
                        self.current_item,
                    )
                )
                self.negotation_state = NegotationState.FINISHED
            elif self.negotation_state == NegotationState.WAITING_FOR_COMMIT:
                self.convinced_agents[message.sender] = True

                if reduce(lambda x, y: x and y, self.convinced_agents.values()):
                    self.negotation_state = NegotationState.FINISHED
        else:
            print("Commit message is not valid")

    def __accept_performative_callback(self, message: Message) -> None:
        """Accept performative callback: the other agent accepts an item."""

        if (
            isinstance(message.content, Item)
            and self.negotation_state == NegotationState.ARGUING
            and self.current_item.name == message.content.name
        ):
            self.convinced_agents[message.sender] = True
            if reduce(lambda x, y: x and y, self.convinced_agents.values()):
                for agent in self.convinced_agents.keys():
                    self.send_message(
                        Message(
                            self.name,
                            agent,
                            MessagePerformative.COMMIT,
                            message.content,
                        )
                    )
                self.negotation_state = NegotationState.WAITING_FOR_COMMIT
                self.convinced_agents = {
                    agent: False for agent in self.convinced_agents.keys()
                }
        else:
            print("Accept message is not valid")

    def __propose_performative_callback(self, message: Message) -> None:
        """Propose performative callback: the other agent proposes an item."""
        self.convinced_agents = {}

        if self.negotation_state != NegotationState.FINISHED:

            if isinstance(
                message.content, Item
            ) and self.preferences.is_item_among_top_10_percent(
                message.content, self.items
            ):
                self.current_item = message.content
                self.__send_accept_message(message.sender)

            elif isinstance(message.content, Item):
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.ASK_WHY,
                        message.content,
                    )
                )
                self.current_item = message.content
                self.negotation_state = NegotationState.ARGUING
        else:
            print("Propose message is not valid")

    def __ask_why_performative_callback(self, message: Message) -> None:
        """Ask why performative callback: The agent other agent sent an ask why message"""
        assert self.negotation_state is not None
        assert isinstance(message.content, Item)

        if (
            self.negotation_state == NegotationState.ARGUING
            and self.current_item.name == message.content.name
        ):
            argument = self.support_proposal(self.current_item)
            self.arguments_used.append(argument)
            self.send_message(
                Message(
                    self.name,
                    message.sender,
                    MessagePerformative.ARGUE,
                    argument,
                )
            )
        else:
            print(self.negotation_state == NegotationState.ARGUING)
            print(self.name, self.current_item, message.content.name)
            print(self.current_item.name != message.content.name)
            print("Ask why message is not valid")

    def __argue_performative_callback(self, message: Message) -> None:
        """Argue performative callback: The agent other agent sent an argue message"""

        if (
            # isinstance(message.content, CriterionValue)
            self.negotation_state == NegotationState.ARGUING
            and self.current_item.name == message.content.item.name
        ):
            self.__send_attack_message(message)

    def __send_propose_message(self, dest: str):
        """Sends a propose message"""
        self.send_message(
            Message(
                self.name,
                dest,
                MessagePerformative.PROPOSE,
                self.current_item,
            )
        )
        self.convinced_agents[dest] = False

    def __send_accept_message(self, dest: str):
        """Sends an accept messsage"""
        self.send_message(
            Message(
                self.name,
                dest,
                MessagePerformative.ACCEPT,
                self.current_item,
            )
        )
        self.negotation_state = NegotationState.WAITING_ANSWER_ACCEPT

    def __send_attack_message(self, message: Message):
        """Send attack message"""
        argument = self.attack_argument(*self.argument_parsing(message.content))
        if argument is None:
            # no attack message was found, propose another item
            if message.content.decision:
                self.__send_accept_message(message.sender)
            else:
                self.current_item = self.get_best_item_to_propose()
                self.__propose_new_item()
        else:
            self.arguments_used.append(argument)
            if argument.item.name == self.current_item.name:
                self.arguments_used.append(argument)
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.ARGUE,
                        argument,
                    )
                )
            else:
                self.current_item = argument.get_item()
                self.__propose_new_item()

    def __argument_was_used(self, argument: Argument) -> bool:
        """Check if the argument was used in the negotiation"""
        if len(self.arguments_used) == 0:
            return False
        for argument_used in self.arguments_used:
            if argument_used.item.name == argument.item.name:
                return True
            if argument_used.premises_couple_values == argument.premises_couple_values:
                return True
            if argument_used.premises_comparison == argument.premises_comparison:
                return True
        return False

    def list_supporting_proposal(self, item: Item):
        """Generate a list of premisses which can be used to support an item
        :param item: Item - name of the item
        :return: list of all premisses PRO an item (sorted by order of importance
        based on agent’s preferences)"""
        return sorted(
            [
                CoupleValue(criterion, self.__preferences.get_value(item, criterion))
                for criterion in self.__preferences.get_criterion_name_list()
                if self.__preferences.get_value(item, criterion).value
                >= Value.GOOD.value
            ],
            key=lambda cv: cv.value.value,  # type: ignore
            reverse=True,
        )

    def list_attacking_proposal(self, item: Item):
        """List attacking proposal"""
        return sorted(
            [
                CoupleValue(criterion, self.__preferences.get_value(item, criterion))
                for criterion in self.__preferences.get_criterion_name_list()
                if self.__preferences.get_value(item, criterion).value
                < Value.GOOD.value
            ],
            key=lambda cv: cv.value.value,  # type: ignore
            reverse=True,
        )

    def support_proposal(self, item: Item) -> Argument:
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: str
         - name of the item which was proposed
        :return: string - the strongest supportive argument
        """
        for couple_value in self.list_supporting_proposal(item):
            arg = Argument(True, item)
            arg.add_premiss_couple_values(couple_value)
            if not self.__argument_was_used(arg):
                self.arguments_used.append(arg)
                return arg

    @staticmethod
    def argument_parsing(
        argument: Argument,
    ):
        """Parse an argument"""
        return (
            argument.premises_comparison,
            argument.premises_couple_values,
            argument.item,
            argument.decision,
        )

    def criterion_is_bad(self, premise: CoupleValue, item: Item) -> bool:
        """Check if a premise is not important"""
        return bool(
            premise.value.value
            < min(
                self.__preferences.get_value(item, premise.criterion_name).value,
                Value.AVERAGE.value,
            )
        )

    def found_better_item_for_criterion(self, premise: CoupleValue, item: Item) -> bool:
        """Found better item for a premise"""
        for item_ in self.items:
            if item_ != item:
                if (
                    self.__preferences.get_value(item_, premise.criterion_name).value
                    > premise.value.value
                ):
                    return True
        return False

    def other_more_important_criterion_is_bad(
        self, premise: CoupleValue, item: Item
    ) -> Optional[CriterionName]:
        """Check if there is another more important criterion"""
        for criterion in self.__preferences.get_criterion_name_list():
            if (
                criterion != premise.criterion_name
                and self.__preferences.get_value(item, criterion).value
                < Value.AVERAGE.value
            ):
                return criterion

        return None

    def other_item_better_on_criterion(self, premise: CoupleValue, item: Item):
        """Other crietrion"""
        for criterion in self.__preferences.get_criterion_name_list():

            if self.__preferences.get_value(item, criterion).value > min(
                Value.GOOD.value,
                min(
                    [
                        self.__preferences.get_value(it, criterion).value
                        for it in self.items
                    ]
                ),
            ):
                return criterion

        return None

    def get_best_criterion(self, item: Item):
        """Get the best criterion for an item"""
        return max(
            self.__preferences.get_criterion_name_list(),
            key=lambda criterion: self.__preferences.get_value(  # type: ignore
                item, criterion
            ).value,
        )

    def argument_is_attackable(self) -> bool:
        """Checks if an argument is attackable"""
