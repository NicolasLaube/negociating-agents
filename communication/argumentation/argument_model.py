"""Argument model"""
# pylint: disable=E0401
import os
from typing import Dict, List, Optional, Tuple

from mesa import Model
from mesa.time import RandomActivation

from communication.argumentation.argument_agent import ArgumentAgent
from communication.argumentation.preferences_generator import load_preferences
from communication.argumentation.states import NegotationState
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
        MessageService(self.schedule)
        self.items = items
        self.criteria = criteria
        self.preferences_folder = preferences_folder
        self.num_agents = number_agents
        self.all_agents: List[ArgumentAgent] = []
        self.commiting = False
        self.agents_history: Dict[int, ArgumentAgent] = {}

    def setup_discussion_between(self, agent_1: int, agent_2: int) -> None:
        """Setup discussion between two agents"""
        self.commiting = False
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
            self.agents_history[agent_id] = agent

    def step(self) -> Tuple[Optional[Item], Optional[ArgumentAgent]]:
        """Step"""
        # self.__messages_service.dispatch_messages()
        self.schedule.step()
        leading_agent = None
        for agent in self.schedule.agents:
            if agent.is_leading:
                leading_agent = agent
        if all(
            agent.negotation_state == NegotationState.FINISHED
            for agent in self.schedule.agents
        ):
            return (self.schedule.agents[0].current_item, leading_agent)
        return None, None
