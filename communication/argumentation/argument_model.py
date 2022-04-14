"""Argument model"""
import os
from typing import List

from mesa import Model
from mesa.time import RandomActivation

from communication.argumentation.argument_agent import ArgumentAgent
from communication.argumentation.preferences_generator import load_preferences
from communication.message.message_service import MessageService
from communication.preferences.criterion_name import CriterionName
from communication.preferences.item import Item


class ArgumentModel(Model):  # pylint: disable=too-many-instance-attributes
    """ArgumentModel which inherit from Model ."""

    def __init__(
        self,
        number_agents: int,
        items: List[Item],
        criteria: List[CriterionName],
        preferences_folder: str,
    ):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.items = items
        self.criteria = criteria
        self.preferences_folder = preferences_folder
        self.num_agents = number_agents
        self.all_agents: List[ArgumentAgent] = []

        self.running = True

    def setup_discussion_between(self, agent_1: int, agent_2: int) -> None:
        """Setup discussion between two agents"""
        for agent in self.all_agents:
            self.schedule.remove(agent)
        self.all_agents = []

        for agent_id in [agent_1, agent_2]:
            preferences = load_preferences(
                os.path.join(self.preferences_folder, f"p{agent_id}.csv")
            )
            agent = ArgumentAgent(
                agent_id, self, f"Agent{agent_id}", self.items, preferences
            )

            self.schedule.add(agent)
            self.all_agents.append(agent)
            print(agent)

    def step(self):
        """Step"""
        self.__messages_service.dispatch_messages()
        self.schedule.step()
