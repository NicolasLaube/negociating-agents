from ast import arg
import csv
from enum import Enum
from functools import reduce
import random
from typing import List, Union, Tuple
from communication.arguments import Argument
from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue
from communication.message.Message import Message

from communication.message.MessagePerformative import MessagePerformative
from communication import Item

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences import (
    Preferences,
    Item,
    CriterionValue,
    CriterionName,
    Value,
)
from communication.arguments.Argument import Argument


class NegotationState(Enum):
    """NegotationState enum class.
    Enumeration containing the possible agent negotiation states.
    """

    REST = 0
    ARGUING = 1
    WAITING_ANSWER_ACCEPT = 2
    WAITING_FOR_COMMIT = 3
    FINISHED = 4


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent ."""

    def __init__(self, unique_id, model, name, items: List[Item]):
        super().__init__(unique_id, model, name)
        self.preferences = None
        self.items = items  # added
        self.negotation_state = NegotationState.REST
        self.proposed_item = None
        self.convinced_agents = None

    def step(self):
        """Step function"""

        # First step: we must begin the conversation
        if self.negotation_state == NegotationState.REST:
            min_id = self.unique_id
            for agent in self.model.schedule.agents:
                min_id = min(min_id, agent.unique_id)
            if min_id == self.unique_id:
                self.convinced_agents = {}
                for agent in self.model.schedule.agents:
                    if agent.get_name() != self.get_name():
                        self.send_message(
                            Message(
                                self.get_name(),
                                agent.get_name(),
                                MessagePerformative.PROPOSE,
                                self.items[0],
                            )
                        )
                        self.convinced_agents[agent.get_name()] = False
                self.negotation_state = NegotationState.ARGUING
                self.proposed_item = self.items[0]

        new_messages = self.get_new_messages()
        for new_message in new_messages:

            # First case: the received item is in the 10% preferred ones
            if new_message.get_performative() == MessagePerformative.PROPOSE:
                self.convinced_agents = None
                if self.negotation_state != NegotationState.FINISHED:
                    if (
                        new_message.get_content()
                        in self.items[: max(1, int(0.1 * len(self.items)))]
                    ):
                        self.send_message(
                            Message(
                                self.get_name(),
                                new_message.get_exp(),
                                MessagePerformative.ACCEPT,
                                new_message.get_content(),
                            )
                        )
                        self.proposed_item = new_message.get_content()
                        self.negotation_state = NegotationState.WAITING_ANSWER_ACCEPT
                    else:
                        self.send_message(
                            Message(
                                self.get_name(),
                                new_message.get_exp(),
                                MessagePerformative.ASK_WHY,
                                new_message.get_content(),
                            )
                        )
                        self.proposed_item = new_message.get_content()
                        self.negotation_state = NegotationState.ARGUING

            # Second case: the other agent sends an accept message
            if new_message.get_performative() == MessagePerformative.ACCEPT:
                if (
                    self.negotation_state == NegotationState.ARGUING
                    and self.proposed_item.get_name()
                    == new_message.get_content().get_name()
                ):
                    self.convinced_agents[new_message.get_exp()] = True
                    if reduce(lambda x, y: x and y, self.convinced_agents.values()):
                        for agent in self.convinced_agents.keys():
                            self.send_message(
                                Message(
                                    self.get_name(),
                                    agent,
                                    MessagePerformative.COMMIT,
                                    new_message.get_content(),
                                )
                            )
                        self.negotation_state = NegotationState.WAITING_FOR_COMMIT
                        self.convinced_agents = {
                            agent: False for agent in self.convinced_agents.keys()
                        }

            # Third case: the other agent sends an ask why message
            if new_message.get_performative() == MessagePerformative.ASK_WHY:
                if (
                    self.negotation_state == NegotationState.ARGUING
                    and self.proposed_item.get_name()
                    == new_message.get_content().get_name()
                ):
                    self.send_message(
                        Message(
                            self.get_name(),
                            new_message.get_exp(),
                            MessagePerformative.ARGUE,
                            self.support_proposal(self.proposed_item),
                        )
                    )

            # Fourth case: the other agent sends an argue why message
            if new_message.get_performative() == MessagePerformative.ARGUE:
                if (
                    self.negotation_state == NegotationState.ARGUING
                    and self.proposed_item.get_name()
                    == new_message.get_content().get_item().get_name()
                ):
                    argument = self.attack_argument(
                        *self.argument_parsing(new_message.get_content())
                    )
                    if argument is None:
                        self.send_message(
                            Message(
                                self.get_name(),
                                new_message.get_exp(),
                                MessagePerformative.ACCEPT,
                                self.proposed_item,
                            )
                        )
                        self.negotation_state = NegotationState.WAITING_ANSWER_ACCEPT
                    else:
                        if (
                            argument.get_item().get_name()
                            == self.proposed_item.get_name()
                        ):
                            self.send_message(
                                Message(
                                    self.get_name(),
                                    new_message.get_exp(),
                                    MessagePerformative.ARGUE,
                                    argument,
                                )
                            )
                        else:
                            self.proposed_item = argument.get_item()
                            self.convinced_agents = {}
                            for agent in self.model.schedule.agents:
                                if agent.get_name() != self.get_name():
                                    self.send_message(
                                        Message(
                                            self.get_name(),
                                            agent.get_name(),
                                            MessagePerformative.PROPOSE,
                                            argument.get_item(),
                                        )
                                    )
                                    self.convinced_agents[agent.get_name()] = False

            # Fifth case: the other agent sends a commit message
            if new_message.get_performative() == MessagePerformative.COMMIT:
                if (
                    self.proposed_item == new_message.get_content()
                    and self.proposed_item.get_name()
                    in [item.get_name() for item in self.items]
                ):
                    if self.negotation_state == NegotationState.WAITING_ANSWER_ACCEPT:
                        self.send_message(
                            Message(
                                self.get_name(),
                                new_message.get_exp(),
                                MessagePerformative.COMMIT,
                                self.proposed_item,
                            )
                        )
                        self.items.pop(
                            [item.get_name() for item in self.items].index(
                                self.proposed_item.get_name()
                            )
                        )
                        self.negotation_state = NegotationState.FINISHED
                    elif self.negotation_state == NegotationState.WAITING_FOR_COMMIT:
                        self.convinced_agents[new_message.get_exp()] = True
                        if reduce(lambda x, y: x and y, self.convinced_agents.values()):
                            self.items.pop(self.items.index(self.proposed_item))
                            self.negotation_state = NegotationState.FINISHED

    def get_preferences(self):
        """Get preference"""
        return self.preferences

    def load_preferences(self, path: str):
        """Load preferences from csv"""
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            categories = next(reader)
            preferences = Preferences()
            preferences.set_criterion_name_list(
                [CriterionName(x) for x in categories[1:]]
            )
            # print("criterion name list ", preferences.criterion_name_list)
            items = []
            for row in reader:
                new_item = Item(row[0], f"This is a {row[0]}")
                items.append(new_item)
                for i, criterion_name in enumerate(categories[1:]):
                    criterion_value = CriterionValue(
                        new_item, CriterionName(criterion_name), Value(int(row[i + 1]))
                    )
                    preferences.add_criterion_value(criterion_value)

            self.preferences = preferences
            self.items = sorted(
                items, key=lambda item: item.get_score(self.preferences), reverse=True
            )

    def generate_random_preferences(
        self, items: List[Item], criteria: List[CriterionName]
    ):
        """Generate preferences"""
        preferences = Preferences()
        random.shuffle(criteria)
        preferences.set_criterion_name_list(criteria)
        for item in items:
            for criterion in criteria:
                preferences.add_criterion_value(
                    CriterionValue(item, criterion, random.choice(list(Value)))
                )
        self.preferences = preferences
        self.items = sorted(
            items, key=lambda item: item.get_score(self.preferences), reverse=True
        )

    def support_proposal(self, item: Item) -> str:
        """
        Used when the agent receives "ASK_WHY" after having proposed an item :param item: str - name of the item which was proposed
        :return: string - the strongest supportive argument
        """
        all_cv = Argument.list_supporting_proposal(item, self.preferences)
        arg = Argument(True, item)
        arg.add_premiss_couple_values(all_cv[0])
        return arg

    def argument_parsing(
        self, argument: Argument
    ) -> Tuple[Union[Comparison, CoupleValue], Item, bool]:
        """Parse an argument"""
        return (
            argument.get_premises_comparison(),
            argument.get_premises_couple_values(),
            argument.get_item(),
            argument.get_decision(),
        )

    def attack_argument(
        self,
        premises_comparison: List[Comparison],
        premises_couple_value: List[CoupleValue],
        item: Item,
        is_chosen: bool,
    ):
        counter_arg = None
        for premise in premises_couple_value:
            # For me, the evaluated criterion is bad
            if is_chosen and premise.value.value < min(
                self.preferences.get_value(item, premise.criterion_name).value,
                Value.AVERAGE.value,
            ):
                if counter_arg == None:
                    counter_arg = Argument(not is_chosen, item)
                counter_arg.add_premiss_couple_values(
                    CoupleValue(
                        premise.criterion_name,
                        self.preferences.get_value(item, premise.criterion_name),
                    )
                )
            # I've found a criterion of better importance that invalidates the goal
            else:
                best_criterion, best_value = None, -1
                for criterion in self.preferences.get_criterion_name_list():
                    if criterion == premise.criterion_name:
                        break
                    if (
                        is_chosen
                        and self.preferences.get_value(item, criterion).value
                        < min(
                            Value.AVERAGE.value,
                            max(
                                [
                                    self.preferences.get_value(it, criterion).value
                                    for it in self.items
                                ]
                            ),
                        )
                    ) or (
                        not is_chosen
                        and self.preferences.get_value(item, criterion).value
                        > max(
                            Value.GOOD.value,
                            min(
                                [
                                    self.preferences.get_value(it, criterion).value
                                    for it in self.items
                                ]
                            ),
                        )
                    ):
                        if counter_arg == None:
                            counter_arg = Argument(not is_chosen, item)
                        counter_arg.add_premiss_couple_values(
                            CoupleValue(
                                criterion, self.preferences.get_value(item, criterion)
                            )
                        )
                        counter_arg.add_premiss_comparison(
                            Comparison(criterion, premise.criterion_name)
                        )
                        break
                    if self.preferences.get_value(item, criterion).value > best_value:
                        best_criterion = criterion
                        best_value = self.preferences.get_value(item, criterion).value
        if counter_arg is not None:
            return counter_arg
        elif not is_chosen:
            argument = Argument(True, item)
            argument.add_premiss_couple_values(
                CoupleValue(
                    best_criterion, self.preferences.get_value(item, best_criterion)
                )
            )
            return argument
        # I've found a better object on the criterion you're talking
        criterion_name = (
            premises_couple_value[0].criterion_name
            if len(premises_couple_value) > 0
            else premises_comparison[0].best_criterion_name
        )
        for new_item in self.items:
            if self.preferences.get_value(
                new_item, criterion_name
            ).value > self.preferences.get_value(
                item, criterion_name
            ).value and new_item.get_score(
                self.preferences
            ) > item.get_score(
                self.preferences
            ):
                counter_arg = Argument(True, new_item)
                counter_arg.add_premiss_couple_values(
                    CoupleValue(
                        criterion_name,
                        self.preferences.get_value(new_item, criterion_name),
                    )
                )
        return counter_arg


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model ."""

    def __init__(
        self, number_agents: int, items: List[Item], criteria: List[CriterionName]
    ):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.items = items
        self.criteria = criteria

        for i in range(1, number_agents + 1):
            agent = ArgumentAgent(i, self, f"Agent{i}", self.items)
            agent.load_preferences(f"data/preferences/p{i}.csv")
            # agent.generate_random_preferences(self.items, self.criteria)
            self.schedule.add(agent)

        self.running = True

    def step(self):
        """Step"""
        self.__messages_service.dispatch_messages()
        self.schedule.step()
