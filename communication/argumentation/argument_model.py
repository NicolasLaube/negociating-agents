"""Argument model"""
from typing import List

from mesa import Model
from mesa.time import RandomActivation

from communication.argumentation.argument_agent import ArgumentAgent
from communication.message.message_service import MessageService
from communication.preferences.criterion_name import CriterionName
from communication.preferences.item import Item


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model ."""

    def __init__(
        self, number_agents: int, items: List[Item], criteria: List[CriterionName]
    ):
        super().__init__()
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
