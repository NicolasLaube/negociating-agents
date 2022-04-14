"""Plot agent preferences"""
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from communication.argumentation.argument_agent import ArgumentAgent


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


def plot_agents_preferences(agents: Dict[int, ArgumentAgent]):
    """Plot agent preferences"""

    items = list(agents.values())[1].items

    items_dict = {item: i for i, item in enumerate(items)}
    _, ax = plt.subplots(figsize=(7, 5))

    agents_preferences: Dict[str, Any] = {
        "Agent": [],
        "Item": [],
        "Scores": [],
    }

    for agent in agents.values():
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
    ax.set_xticks(list(range(len(items))))
    ax.set_xticklabels([str(item) for item in items])

    plt.show()
