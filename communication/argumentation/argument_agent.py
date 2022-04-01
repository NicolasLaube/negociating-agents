"""Argument agent"""
# pylint: disable=W0631
import csv
import random
from functools import reduce
from typing import Dict, List, Optional

from communication.agent.communicating_agent import CommunicatingAgent
from communication.argumentation.states import NegotationState
from communication.arguments.argument import Argument
from communication.arguments.comparison import Comparison
from communication.arguments.couple_value import CoupleValue
from communication.message.message import Message
from communication.message.message_performative import MessagePerformative
from communication.preferences import (
    CriterionName,
    CriterionValue,
    Item,
    Preferences,
    Value,
)


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
        print([item.get_score(self.__preferences) for item in self.items])
        self.negotation_state = NegotationState.REST
        self.favorite_item = self.items[0]
        self.convinced_agents: Dict[str, bool] = {}
        self.arguments_used = []
        self.item_was_proposed = False

    def __str__(self) -> str:
        return f"""
        Secret presentation (only you are seeing it):
        ---------------------------------------------
        My name is Agent {self.name}
        My favorite item is {self.favorite_item} with score {self.favorite_item.get_score(self.__preferences)}
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
                self.__argue_performative_callback(new_message)

            # Fifth case: the other agent sends a commit message
            elif new_message.performative == MessagePerformative.COMMIT:
                self.__commit_performative_callback(new_message)

    def __start_conversation(self):
        """Start conversation"""
        min_id = self.unique_id
        for agent in self.model.schedule.agents:
            min_id = min(min_id, agent.unique_id)

        # Agent with min id starts the conversation
        if min_id == self.unique_id:
            self.convinced_agents = {}
            for agent in self.model.schedule.agents:
                if agent.name != self.name:
                    self.send_message(
                        Message(
                            self.name,
                            agent.name,
                            MessagePerformative.PROPOSE,
                            self.favorite_item,
                        )
                    )
                    self.item_was_proposed = True
                    self.convinced_agents[agent.name] = False
            self.negotation_state = NegotationState.ARGUING
            # self.favorite_item = self.items[0]

    def __commit_performative_callback(self, message: Message) -> None:
        """Commit performative callback: the other agent commits an item."""

        if self.favorite_item == message.content and self.favorite_item.name in [
            item.name for item in self.items
        ]:
            if self.negotation_state == NegotationState.WAITING_ANSWER_ACCEPT:
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.COMMIT,
                        self.favorite_item,
                    )
                )
                self.items.pop(
                    [item.name for item in self.items].index(self.favorite_item.name)
                )
                self.negotation_state = NegotationState.FINISHED
            elif self.negotation_state == NegotationState.WAITING_FOR_COMMIT:
                self.convinced_agents[message.sender] = True

                if reduce(lambda x, y: x and y, self.convinced_agents.values()):
                    self.items.pop(self.items.index(self.favorite_item))
                    self.negotation_state = NegotationState.FINISHED
        else:
            print("Commit message is not valid")

    def __accept_performative_callback(self, message: Message) -> None:
        """Accept performative callback: the other agent accepts an item."""

        if (
            isinstance(message.content, Item)
            and self.negotation_state == NegotationState.ARGUING
            and self.favorite_item.name == message.content.name
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
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.ACCEPT,
                        message.content,
                    )
                )
                # self.favorite_item = message.content
                self.negotation_state = NegotationState.WAITING_ANSWER_ACCEPT
            elif isinstance(message.content, Item):
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.ASK_WHY,
                        message.content,
                    )
                )
                # self.favorite_item = message.content
                self.negotation_state = NegotationState.ARGUING
        else:
            print("Propose message is not valid")

    def __ask_why_performative_callback(self, message: Message) -> None:
        """Ask why performative callback: The agent other agent sent an ask why message"""
        assert self.negotation_state is not None

        if (
            isinstance(message.content, Item)
            and self.negotation_state == NegotationState.ARGUING
            and self.favorite_item.name == message.content.name
        ):
            argument = self.support_proposal(self.favorite_item)
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
            print(self.name, self.favorite_item, message.content.name)
            print(self.favorite_item.name != message.content.name)
            print("Ask why message is not valid")

    def __proprose_my_favorite_item_if_not_already(self, agent_name: str):
        """Propose my favorite item if not proposed before"""
        if not self.item_was_proposed:
            self.send_message(
                Message(
                    self.name,
                    agent_name,
                    MessagePerformative.PROPOSE,
                    self.favorite_item,
                )
            )
            self.item_was_proposed = True

    def __argue_performative_callback(self, message: Message) -> None:
        """Argue performative callback: The agent other agent sent an argue message"""

        if (
            isinstance(message.content, CriterionValue)
            and self.negotation_state == NegotationState.ARGUING
            and self.favorite_item.name == message.content.item.name
        ):
            argument = self.attack_argument(*self.argument_parsing(message.content))
            self.arguments_used.append(argument)

            self.__proprose_my_favorite_item_if_not_already(agent.name)

            if argument is None:
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.ACCEPT,
                        self.favorite_item,
                    )
                )
                self.negotation_state = NegotationState.WAITING_ANSWER_ACCEPT

            elif argument.item.name == self.favorite_item.name:
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
                self.favorite_item = argument.get_item()
                self.convinced_agents = {}
                for agent in self.model.schedule.agents:
                    if agent.name != self.name:
                        self.send_message(
                            Message(
                                self.name,
                                agent.name,
                                MessagePerformative.PROPOSE,
                                argument.get_item(),
                            )
                        )
                        self.convinced_agents[agent.name] = False

        elif isinstance(message.content, Argument):
            if not self.item_was_proposed:
                self.send_message(
                    Message(
                        self.name,
                        message.sender,
                        MessagePerformative.PROPOSE,
                        self.favorite_item,
                    )
                )
                self.item_was_proposed = True
                return

            counter_argument = self.attack_argument(
                *self.argument_parsing(message.content)
            )
            self.arguments_used.append(counter_argument)

            self.send_message(
                Message(
                    self.name,
                    message.sender,
                    MessagePerformative.ARGUE,
                    counter_argument,
                )
            )

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

    def other_more_important_criterion_is_bad(self, premise: CoupleValue, item: Item):
        """Check if there is another more important criterion"""
        for criterion in self.__preferences.get_criterion_name_list():
            if (
                criterion != premise.criterion_name
                and self.__preferences.get_value(item, criterion).value
                < Value.AVERAGE.value
            ):
                return criterion

        return None

    def other_crietrion_nice(self, premise: CoupleValue, item: Item):
        """Other crietrion"""
        for criterion in self.__preferences.get_criterion_name_list():

            if self.__preferences.get_value(item, criterion).value > max(
                Value.GOOD.value,
                min(
                    [
                        self.__preferences.get_value(it, criterion).value
                        for it in self.items
                    ]
                ),
            ):
                print(criterion)
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
                bad_criterion = self.other_more_important_criterion_is_bad(
                    premise, item
                )

                # For me, the evaluated criterion is bad
                if self.criterion_is_bad(premise, item):
                    counter_argument = argue_criterion_is_bad(counter_argument)

                # I prefer another item who is better for this criterion
                if self.found_better_item_for_criterion(premise, item):
                    counter_argument = argue_found_better_item_for_criterion(
                        counter_argument
                    )

                if bad_criterion is not None:
                    counter_argument = (
                        argue_found_other_more_important_criterion_is_bad(
                            counter_argument, bad_criterion
                        )
                    )
            else:
                nice_criterion = self.other_crietrion_nice(premise=premise, item=item)

                if nice_criterion is not None:

                    counter_argument = argue_found_other_more_important_criterion_is_bad(
                        counter_argument, nice_criterion
                    )
                else:
                    print("not enough cc")
                    return self.support_proposal(item)
            # I've found a criterion of better importance that invalidates the goal
            # else:
            #     best_criterion, best_value = None, -1

            #     for criterion in self.__preferences.get_criterion_name_list():
            #         # if criterion == premise.criterion_name:
            #         #     break
            #         # if (
            #     if criterion != premise.criterion_name and self.__preferences.get_value(
            #     item, criterion
            # ).value < min(
            #     Value.AVERAGE.value,
            #     max(
            #         [
            #             self.__preferences.get_value(it, criterion).value
            #             for it in self.items
            #         ]
            #     ),
            # )
            #         # ) or (
            #         #     not is_chosen
            #         #     and self.__preferences.get_value(item, criterion).value
            #         #     > max(
            #         #         Value.GOOD.value,
            #         #         min(
            #         #             [
            #         #                 self.__preferences.get_value(it, criterion).value
            #         #                 for it in self.items
            #         #             ]
            #         #         ),
            #         #     )
            #         # ):
            #         #     if counter_argument is None:
            #         #         counter_argument = Argument(not is_chosen, item)
            #         #     counter_argument.add_premiss_couple_values(
            #         #         CoupleValue(
            #         #             criterion, self.__preferences.get_value(item, criterion)
            #         #         )
            #         #     )
            #         #     counter_argument.add_premiss_comparison(
            #         #         Comparison(criterion, premise.criterion_name)
            #         #     )
            #         #     break
            #         if self.preferences.get_value(item, criterion).value > best_value:
            #             best_criterion = criterion
            #             best_value = self.preferences.get_value(item, criterion).value

        # best_criterion = self.get_best_criterion(item)

        # if counter_argument is not None:
        #     return counter_argument
        # if not is_chosen:
        #     argument = Argument(True, item)
        #     argument.add_premiss_couple_values(
        #         CoupleValue(
        #             best_criterion, self.preferences.get_value(item, best_criterion)
        #         )
        #     )
        #     return argument
        # # I've found a better object on the criterion you're talking
        # criterion_name = (
        #     premises_couple_value[0].criterion_name
        #     if len(premises_couple_value) > 0
        #     else premises_comparison[0].best_criterion_name
        # )
        # for new_item in self.items:
        #     if self.__preferences.get_value(
        #         new_item, criterion_name
        #     ).value > self.__preferences.get_value(
        #         item, criterion_name
        #     ).value and new_item.get_score(
        #         self.__preferences
        #     ) > item.get_score(
        #         self.__preferences
        #     ):
        #         counter_argument = Argument(True, new_item)
        #         counter_argument.add_premiss_couple_values(
        #             CoupleValue(
        #                 criterion_name,
        #                 self.__preferences.get_value(new_item, criterion_name),
        #             )
        #         )
        return counter_argument
