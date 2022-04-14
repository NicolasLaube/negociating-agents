"""Main script for the communication."""
from argparse import ArgumentParser
from itertools import combinations

from communication import config
from communication.argumentation.argument_model import ArgumentModel
from communication.preferences.criterion_name import CriterionName

if __name__ == "__main__":
    print("Testing two agents communication")

    argparser = ArgumentParser()
    argparser.add_argument(
        "--mode",
        type=str,
        default="presidential",
        help="Argumentation mode (presidential or cars)",
    )
    argparser.add_argument(
        "--num_agents",
        type=int,
        default=3,
        help="Number of agents in the argumentation",
    )

    argparser.add_argument(
        "--max_num_steps",
        type=int,
        default=100,
        help="Maximum number of steps in the argumentation",
    )

    NUM_AGENTS = argparser.parse_args().num_agents

    if argparser.parse_args().mode == "presidential":

        argument_model = ArgumentModel(
            2,
            items=config.PRESIDENTIAL_ITEMS,
            criteria=CriterionName.list_presidential(),
            preferences_folder=config.PRESIDENTIAL_PREFERENCES_FOLDER,
        )

    elif argparser.parse_args().mode == "cars":

        argument_model = ArgumentModel(
            2,
            items=config.CAR_ITEMS,
            criteria=CriterionName.list_cars(),
            preferences_folder=config.CARS_PREFERENCES_FOLDER,
        )

    for agent_1, agent_2 in combinations(list(range(1, NUM_AGENTS + 1)), 2):
        print(f"NEGOCIATION BETWEEN {agent_1} AND {agent_2}:")
        argument_model.setup_discussion_between(agent_1, agent_2)

        for _ in range(argparser.parse_args().max_num_steps):
            argument_model.step()
