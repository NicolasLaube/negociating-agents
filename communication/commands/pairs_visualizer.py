"""Pairs visualizer"""
from itertools import combinations

from communication import config
from communication.argumentation.argument_model import ArgumentModel
from communication.visualization.plot_result_graph import plot_pair_result_graph


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
                        "chosen_item": chosen_item,
                        "arguments": leading_agent.list_supporting_proposal(
                            chosen_item
                        ),
                    }
                )
                break
    print("\nRESULTS:")
    print(results)

    plot_pair_result_graph(argument_model.agents_history, results)
