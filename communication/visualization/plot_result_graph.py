"""Plot pair result graph"""
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout

from communication import config
from communication.argumentation.argument_agent import ArgumentAgent


def plot_pair_result_graph(
    agents: Dict[int, ArgumentAgent], results: List[Dict[str, Any]]
):
    """Plot winning graph"""

    def get_node_label(agent_id: int) -> str:
        """Get node label"""
        return f"A{agent_id}"

    graph = nx.DiGraph()

    # Add the agents
    node_color_map = []
    for agent_id, agent in agents.items():
        graph.add_node(get_node_label(agent_id), fillcolor="white")
        node_color_map.append(config.ITEM_COLORS[agent.items[0].name])

    # Add the winning pairs
    edge_labels = {}
    edge_color_map = {}
    for result in results:
        graph.add_edge(
            get_node_label(result["winning_agent"]),
            get_node_label(result["losing_agent"]),
        )
        edge_labels[
            (
                get_node_label(result["winning_agent"]),
                get_node_label(result["losing_agent"]),
            )
        ] = str(result["chosen_item"])
        edge_color_map[
            (
                get_node_label(result["winning_agent"]),
                get_node_label(result["losing_agent"]),
            )
        ] = config.ITEM_COLORS[result["chosen_item"].name]

    pos = graphviz_layout(graph, prog="circo")
    nx.draw(
        graph,
        with_labels=True,
        pos=pos,
        font_weight="bold",
        font_color="white",
        arrowsize=20,
        node_color=node_color_map,
        edge_color=[edge_color_map[(u, v)] for u, v in graph.edges],
        node_size=800,
    )
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_color="black",
    )

    plt.show()
