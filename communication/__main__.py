"""Main script for the communication."""
from argparse import ArgumentParser
from itertools import combinations

from communication import config
from communication.argumentation.argument_model import ArgumentModel
from communication.preferences.criterion_name import CriterionName
from communication.commands.pairs_visualizer import visualize_pairs_negociations

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

    visualize_pairs_negociations(argument_model, NUM_AGENTS)
