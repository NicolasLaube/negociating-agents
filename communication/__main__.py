"""Main script for the communication."""
from communication.argumentation.argument_model import ArgumentModel
from communication.preferences.criterion_name import CriterionName
from communication import config

print("Testing two agents communication")

argument_model = ArgumentModel(
    2, items=config.PRESIDENTIAL_ITEMS, criteria=CriterionName.list_presidential()
)

NUM_STEPS = 100


for _ in range(NUM_STEPS):
    argument_model.step()
