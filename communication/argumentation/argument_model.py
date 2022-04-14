"""Argument model"""
# pylint: disable=E0401
import os
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from mesa import Model
from mesa.time import RandomActivation

from communication.argumentation.argument_agent import ArgumentAgent
from communication.argumentation.preferences_generator import load_preferences
from communication.argumentation.states import NegotationState
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
        # self.__messages_service = MessageService(self.schedule)
        self.items = items
        self.criteria = criteria
        self.preferences_folder = preferences_folder
        self.num_agents = number_agents
        self.all_agents: List[ArgumentAgent] = []
        self.commiting = False

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

        plot_agents_preferences(self.all_agents)

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


def plot_one_agent_preferences(agent: ArgumentAgent):
    """Plot agent preferences"""

    agent_scores = []

    items = list(range(len(agent.items)))

    for item in agent.items:
        agent_scores.append(item.get_score(agent.preferences))

    _, ax = plt.subplots(figsize=(7, 5))

    sns.set(font_scale=1.5)

    sns.barplot(x=items, y=agent_scores)

    ax.set_xticklabels([str(item) for item in agent.items])

    plt.show()


def plot_agents_preferences(agents: List[ArgumentAgent]):
    """Plot agent preferences"""

    items_dict = {item: i for i, item in enumerate(agents[0].items)}
    _, ax = plt.subplots(figsize=(7, 5))

    agents_preferences: Dict[str, Any] = {
        "Agent": [],
        "Item": [],
        "Scores": [],
    }

    for agent in agents:
        scores = [
            (item.get_score(agent.preferences), item) for item in items_dict.keys()
        ]
        for score, item in scores:
            for _ in range(int(score)):
                agents_preferences["Scores"].append(1)
                agents_preferences["Agent"].append(agent.name)
                agents_preferences["Item"].append(items_dict[item])

    df = pd.DataFrame(agents_preferences)

    sns.histplot(df, x="Item", hue="Agent", multiple="dodge")
    ax.set_xticks(list(range(len(agents[0].items))))
    ax.set_xticklabels([str(item) for item in agents[0].items])

    plt.show()
