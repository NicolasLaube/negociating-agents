from enum import Enum
from functools import reduce
import random
import numpy as np
from typing import List
from communication.message.Message import Message

from communication.message.MessagePerformative import MessagePerformative
from communication import Item
from communication.preferences import CriterionName, Value

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Preferences import Preferences


class NegotationState(Enum):
    """NegotationState enum class.
    Enumeration containing the possible agent negotiation states.
    """

    REST = 0
    CONVINCING_AGENTS = 1
    WAITING_ANSWER_COMMIT = 2
    WAITING_ANSWER_ACCEPT = 3
    WAITING_ANSWER_WHY = 4
    FINISHED = 5


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
                self.negotation_state = NegotationState.CONVINCING_AGENTS
                self.proposed_item = self.items[0]

        new_messages = self.get_new_messages()
        for new_message in new_messages:

            # First case: the received item is in the 10% preferred ones
            if new_message.get_performative() == MessagePerformative.PROPOSE:
                if self.negotation_state != NegotationState.CONVINCING_AGENTS:
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
                        self.negotation_state = NegotationState.WAITING_ANSWER_WHY

            # Second case: the other agent sends an accept message
            if new_message.get_performative() == MessagePerformative.ACCEPT:
                if (
                    self.negotation_state == NegotationState.CONVINCING_AGENTS
                    and self.proposed_item == new_message.get_content()
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
                        self.negotation_state = NegotationState.WAITING_ANSWER_COMMIT
                        self.convinced_agents = {
                            agent: False for agent in self.convinced_agents.keys()
                        }

            # Third case: the other agent sends an ask why message
            if new_message.get_performative() == MessagePerformative.ASK_WHY:
                if (
                    self.negotation_state == NegotationState.CONVINCING_AGENTS
                    and self.proposed_item == new_message.get_content()
                ):
                    self.send_message(
                        Message(
                            self.get_name(),
                            new_message.get_exp(),
                            MessagePerformative.ARGUE,
                            None,
                        )
                    )

            # Fourth case: the other agent sends a commit message
            if new_message.get_performative() == MessagePerformative.COMMIT:
                if (
                    self.proposed_item == new_message.get_content()
                    and self.proposed_item in self.items
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
                        self.items.pop(self.items.index(self.proposed_item))
                        self.negotation_state = NegotationState.FINISHED
                    elif self.negotation_state == NegotationState.WAITING_ANSWER_COMMIT:
                        self.convinced_agents[new_message.get_exp()] = True
                        if reduce(lambda x, y: x and y, self.convinced_agents.values()):
                            self.items.pop(self.items.index(self.proposed_item))
                            self.negotation_state = NegotationState.FINISHED

    def get_preferences(self):
        """Get preference"""
        return self.preferences

    def generate_preferences(self, items: List[Item], criteria: List[CriterionName]):
        """Generate preferences"""
        # TODO verify code create better preferences
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
            agent.generate_preferences(self.items, self.criteria)
            self.schedule.add(agent)

        self.running = True

    def step(self):
        """Step"""
        self.__messages_service.dispatch_messages()
        self.schedule.step()
