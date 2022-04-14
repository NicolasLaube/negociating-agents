"""Pairs visualizer"""
from typing import Any, Dict, List
import seaborn as sns
import pandas as pd
from itertools import combinations
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
from communication.argumentation.argument_model import ArgumentModel
from communication import config
from communication.argumentation.argument_agent import ArgumentAgent


def visualize_pairs_negociations(argument_model: ArgumentModel, num_agents: int):
    """Visualize pairs negociation"""
    results = []
    for agent_1, agent_2 in combinations(list(range(1, num_agents + 1)), 2):

        print(f"\nNEGOCIATION BETWEEN {agent_1} AND {agent_2}:")
        argument_model.setup_discussion_between(agent_1, agent_2)

        for _ in range(config.MAX_NUM_STEPS):
            chosen_item, leading_agent = argument_model.step()
            if chosen_item is not None:
                results.append(
                    {
                        "winning_agent": leading_agent.unique_id,
                        "losing_agent": agent_1
                        if agent_1 != leading_agent.unique_id
                        else agent_2,
                        "chosen_item": str(chosen_item),
                        "arguments": [
                            str(arg)
                            for arg in leading_agent.list_supporting_proposal(
                                chosen_item
                            )
                        ],
                    }
                )
                break
    print(results)

    plot_winning_graph(num_agents, results)


def plot_winning_graph(num_agents: int, results: List[Dict[str, Any]]):
    """Plot winning graph"""

    def get_node_label(agent_id: int) -> str:
        """Get node label"""
        return f"{agent_id}"

    G = nx.Graph()

    color_map = []

    # # Add the agents
    # for agent_id in range(1, num_agents + 1):
    #     G.add_node(get_node_label(agent_id))

    # Add the winning pairs
    edge_labels = {}
    for result in results:
        G.add_edge(
            get_node_label(result["winning_agent"]),
            get_node_label(result["losing_agent"]),
            # label=str(result["chosen_item"]),
        )
        edge_labels[
            (
                get_node_label(result["winning_agent"]),
                get_node_label(result["losing_agent"]),
            )
        ] = str(result["chosen_item"])

    # pos = graphviz_layout(G, prog="circo")
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos=pos,
        # with_labels=False,
        # node_color=color_map,
        font_weight="bold",
        arrowsize=10,
        labels={node: node for node in G.nodes()},
    )
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_color="black",
    )

    nx.draw_networkx_labels(G, pos, horizontalalignment="left")
    plt.show()
