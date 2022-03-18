import random
import numpy as np
from typing import List
from communication.message.Message import Message

from communication.message.MessagePerformative import MessagePerformative
from communication import Item, preferences
from communication.preferences import CriterionName

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.Preferences import Preferences


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent ."""

    def __init__(self, unique_id, model, name, items: List[Item]):
        super().__init__(unique_id, model, name)
        self.preference = None
        self.items = items  # added

    def step(self):
        """Step function"""
        if self.unique_id == 1:  # agent 2s

            self.get_messages_from_performative(
                performative=MessagePerformative.PROPOSE
            )

            new_messages = self.get_new_messages()
            if len(new_messages) > 0:
                message = Message(
                    "Agent1", "Agent2", MessagePerformative.PROPOSE, "Item1"
                )
                self.send_message(message=message)

        else:  # agent 1

            self.get_messages_from_performative(
                performative=MessagePerformative.PROPOSE
            )

    def get_preference(self):
        """Get preference"""
        return self.preference

    def generate_preferences(self, items: List[Item], criterion: List[CriterionName]):
        """Generate preferences"""
        # TODO verify code create better preferences
        preferences = np.zeros([len(items), len(criterion)])
        for i, _ in enumerate(items):
            for j, _ in enumerate(criterion):
                preferences[i, j] = random.randint(0, 5)
        self.preference = preferences


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model ."""

    def __init__(self, number_agents: int, items: List[Item]):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.items = items

        for i in range(1, number_agents + 1):
            agent = ArgumentAgent(i, self, f"Agent{i}")
            agent.generate_preferences(self.items)
            self.schedule.add(agent)

        self.running = True

    def step(self):
        """Step"""
        self.__messages_service.dispatch_messages()
        self.schedule.step()
