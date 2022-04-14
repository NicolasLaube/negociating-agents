"""Argument agent"""
# pylint: disable=W0631,W0612,R0902, E0401
from functools import reduce
from typing import Dict, List, Optional

from communication import config
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
        self.proposed_items: List[Item] = []
        self.negotation_state = NegotationState.REST
        self.current_item: Optional[Item] = None
        self.convinced_agents: Dict[str, bool] = {}
        self.arguments_used: List[Argument] = []
        self.percentage = config.INITIAL_PERCENTAGE

    def __str__(self) -> str:
        return f"""
        Secret presentation (only you are seeing it):
        ---------------------------------------------
        My name is Agent {self.name}
        My favorite item is {self.items[0]} with score {self.items[0].get_score(self.__preferences)}
        My preferences list is {" > ".join([str(item) for item in self.items])}
        """

    @property
    def preferences(self) -> Preferences:
        """Get preferences"""
        return self.__preferences

    def step(self) -> None:
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
                self.__argue_performative_callback(new_message)

            # Fifth case: the other agent sends a commit message
            elif new_message.performative == MessagePerformative.COMMIT:
                self.__commit_performative_callback(new_message)

            elif new_message.performative == MessagePerformative.NOT_AGREE:
                self.__loose_constraints()
                if self.current_item is None:
                    self.current_item = self.__get_best_item_to_propose()

                self.__propose_new_item()

    def __get_attack_argument(
        self,
        premises_couple_value: List[CoupleValue],
        item: Item,
        is_chosen: bool,
    ) -> Optional[Argument]:
        """Attack argument"""

        def add_couple_value_to_arg(
            arg: Optional[Argument], criterion_name: CriterionName
        ) -> Optional[Argument]:
            """Arguments for found other more important criterion"""
            if arg is None:
                arg = Argument(not is_chosen, item)

            arg.add_premiss_couple_values(
                CoupleValue(
                    criterion_name, self.__preferences.get_value(item, criterion_name)
                )
            )

            if not self.__argument_was_used(arg):
                return arg
            return None

        def add_coupe_value_and_comparison_to_arg(
            arg: Optional[Argument], criterion_name: CriterionName
        ) -> Optional[Argument]:
            """Arguments for found other more important criterion"""
            if arg is None:
                arg = Argument(not is_chosen, item)

            arg.add_premiss_couple_values(
                CoupleValue(
                    criterion_name, self.__preferences.get_value(item, criterion_name)
                )
            )

            arg.add_premiss_comparison(
                Comparison(criterion_name, premise.criterion_name)
            )

            if not self.__argument_was_used(arg):
                return arg
            return None

        def arg_other_item(
            arg: Optional[Argument],
            item: Item,
        ) -> Optional[Argument]:
            """Arguments for found other item"""
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

        counter_argument: Optional[Argument] = None

        for premise in premises_couple_value:  # couple criterion value

            if is_chosen:
                # Another more important criterion is bad
                counter_argument = self.other_more_important_criterion_is_bad(
                    premise, item, is_chosen
                )
                # if bad_criterion is not None:
                #     counter_argument = add_couple_value_to_arg(
                #         counter_argument, bad_criterion
                #     )
                #     print(counter_argument)

                # For me, the evaluated criterion is bad
                if counter_argument is None and self.criterion_is_bad(premise, item):
                    counter_argument = add_couple_value_to_arg(
                        counter_argument, premise.criterion_name
                    )

                # I prefer another item which is better for this criterion
                better_item = self.get_better_item_for_criterion(premise, item)
                if counter_argument is None and better_item is not None:
                    counter_argument = arg_other_item(counter_argument, better_item)

                if counter_argument is not None:
                    return counter_argument

                return None

            other_item_better_on_crietrion = self.other_criterion_is_better(
                premise=premise, item=item
            )

            if other_item_better_on_crietrion is not None:

                return add_coupe_value_and_comparison_to_arg(
                    counter_argument, other_item_better_on_crietrion
                )
            # VERIFY the loop is correct !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        return None

    def __get_best_item_to_propose(self) -> Optional[Item]:
        """Get best item to propose that wasn't already proposed"""
        for item in self.items:
            if (
                item.name not in self.proposed_items
                and self.preferences.is_item_among_top_percent(
                    item, self.items, self.percentage
                )
            ):
                self.proposed_items.append(item.name)
                return item
        return None

    def __loose_constraints(self) -> None:
        """Loose teh constraints"""
        self.proposed_items = []

        self.negotation_state = NegotationState.ARGUING
        self.percentage += config.INCREASE_PERCENTAGE
        self.current_item = None
        self.convinced_agents = {}
        self.arguments_used = []
        # percentage of items that are ok is increased

    def __propose_new_item(self) -> None:
        """Propose new item"""
        self.convinced_agents = {}
        for agent in self.model.schedule.agents:
            if agent.name != self.name:
                self.__send_propose_message(agent.name)
        self.negotation_state = NegotationState.ARGUING

    def __start_conversation(self) -> None:
        """Start conversation"""
        min_id = self.unique_id
        for agent in self.model.schedule.agents:
            min_id = min(min_id, agent.unique_id)

        # Agent with min id starts the conversation
        if min_id == self.unique_id:
            self.current_item = self.__get_best_item_to_propose()
            self.__propose_new_item()

    def __commit_performative_callback(self, message: Message) -> None:
        """Commit performative callback: the other agent commits an item."""
        if self.current_item is None:
            raise ValueError("Current item is None")

        if (
            isinstance(message.content, Item)
            and self.current_item.name == message.content.name
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
            raise ValueError("Commit message is not valid")

    def __accept_performative_callback(self, message: Message) -> None:
        """Accept performative callback: the other agent accepts an item."""
        if self.current_item is None:
            raise ValueError("Current item is None")

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
            raise ValueError("Accept message is not valid")

    def __propose_performative_callback(self, message: Message) -> None:
        """Propose performative callback: the other agent proposes an item."""
        self.convinced_agents = {}

        if self.negotation_state != NegotationState.FINISHED:

            if isinstance(
                message.content, Item
            ) and self.preferences.is_item_among_top_percent(
                message.content, self.items, self.percentage
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
            raise ValueError("Propose message is not valid")

    def __ask_why_performative_callback(self, message: Message) -> None:
        """Ask why performative callback: The agent other agent sent an ask why message"""
        # assert self.negotation_state is not None

        if self.current_item is None:
            raise ValueError("Current item is None")

        if (
            isinstance(message.content, Item)
            and self.negotation_state == NegotationState.ARGUING
            and self.current_item.name == message.content.name
        ):
            argument = self.support_proposal(self.current_item)

            if argument is not None:

                self.arguments_used.append(argument)
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.ARGUE,
                        argument,
                    )
                )
                return
        raise ValueError("Ask why message is not valid")

    def __argue_performative_callback(self, message: Message) -> None:
        """Argue performative callback: The agent other agent sent an argue message"""
        assert isinstance(
            message.content, Argument
        ), "Message content should be an Argument"

        if self.current_item is None:
            raise ValueError("Current item is None")

        if (
            self.negotation_state == NegotationState.ARGUING
            and self.current_item.name == message.content.item.name
        ):
            self.__send_attack_message(message)

    def __send_propose_message(self, dest: str) -> None:
        """Sends a propose message"""

        if self.current_item is None:
            self.__send_not_agree(dest)
            return

        self.send_message(
            Message(
                self.name,
                dest,
                MessagePerformative.PROPOSE,
                self.current_item,
            )
        )
        self.convinced_agents[dest] = False

    def __send_accept_message(self, dest: str) -> None:
        """Sends an accept messsage"""
        if self.current_item is None:
            raise ValueError("Current item is None")

        self.send_message(
            Message(
                self.name,
                dest,
                MessagePerformative.ACCEPT,
                self.current_item,
            )
        )
        self.negotation_state = NegotationState.WAITING_ANSWER_ACCEPT

    def __send_not_agree(self, dest: str) -> None:
        """Sends an not agree message"""
        self.__loose_constraints()
        self.send_message(
            Message(
                self.name,
                dest,
                MessagePerformative.NOT_AGREE,
                "We have to loose our constraints",
            )
        )

    def __send_attack_message(self, message: Message) -> None:
        """Send attack message"""
        assert isinstance(
            message.content, Argument
        ), "Message content should be an Argument"

        argument = self.__get_attack_argument(
            message.content.premises_couple_values,
            message.content.item,
            message.content.decision,
        )

        if argument is None:
            # no attack message was found, propose another item
            self.current_item = self.__get_best_item_to_propose()

            if self.current_item is not None:
                self.__propose_new_item()
            else:
                self.__send_not_agree(message.sender)

        else:
            if self.current_item is None:
                raise ValueError("Current item is None")

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
                self.current_item = argument.item
                self.__propose_new_item()

    def __argument_was_used(self, argument: Argument) -> bool:
        """Check if the argument was used in the negotiation"""
        if len(self.arguments_used) == 0:
            return False
        for argument_used in self.arguments_used:
            if (
                argument_used.item.name == argument.item.name
                and argument_used.premises_couple_values
                == argument.premises_couple_values
                and argument_used.premises_comparison == argument.premises_comparison
            ):
                return True
        return False

    def list_supporting_proposal(self, item: Item) -> List[CoupleValue]:
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

    def list_attacking_proposal(self, item: Item) -> List[CoupleValue]:
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

    def support_proposal(self, item: Item) -> Optional[Argument]:
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
        return None

    def criterion_is_bad(self, premise: CoupleValue, item: Item) -> bool:
        """Check if a premise is not important"""
        return bool(
            premise.value.value
            < min(
                self.__preferences.get_value(item, premise.criterion_name).value,
                Value.AVERAGE.value,
            )
        )

    def get_better_item_for_criterion(
        self, premise: CoupleValue, item: Item
    ) -> Optional[Item]:
        """Found better item for a premise"""
        for item_ in self.items:
            if item_ != item:
                if (
                    self.__preferences.get_value(item_, premise.criterion_name).value
                    > premise.value.value
                ):
                    return item_
        return None

    def other_more_important_criterion_is_bad(
        self, premise: CoupleValue, item: Item, is_chosen: bool
    ) -> Optional[Argument]:
        """Check if there is another more important criterion"""
        for criterion in self.__preferences.get_criterion_name_list():
            if (
                criterion != premise.criterion_name
                and self.__preferences.get_value(item, criterion).value
                < Value.AVERAGE.value
            ):
                arg = Argument(not is_chosen, item)

                arg.add_premiss_couple_values(
                    CoupleValue(
                        criterion, self.__preferences.get_value(item, criterion)
                    )
                )

                arg.add_premiss_comparison(
                    Comparison(criterion, premise.criterion_name)
                )

                if not self.__argument_was_used(arg):
                    return arg

        return None

    def other_criterion_is_better(self, premise: CoupleValue, item: Item):
        """Other criterion"""
        for criterion in self.__preferences.get_criterion_name_list():

            if criterion.name == premise.criterion_name:
                break

            if self.__preferences.get_value(item, criterion).value > min(
                Value.AVERAGE.value,
                min(
                    [
                        self.__preferences.get_value(item_, criterion).value
                        for item_ in self.items
                        if self.__preferences.get_value(item_, criterion) is not None
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
