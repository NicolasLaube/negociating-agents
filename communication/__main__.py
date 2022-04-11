"""Main script for the communication."""
from communication import Item
from communication.argumentation.argument_model import ArgumentModel
from communication.preferences.criterion_name import CriterionName

print("Testing two agents communication")


e_car = Item("E", "The nice electric car")
diesel_car = Item("ICED", "The greate diesel car")

ITEMS = [e_car, diesel_car]
CRITERIA = [
    CriterionName.CONSUMPTION,
    CriterionName.DURABILITY,
    CriterionName.ENVIRONMENT_IMPACT,
    CriterionName.NOISE,
    CriterionName.PRODUCTION_COST,
]

argument_model = ArgumentModel(2, items=ITEMS, criteria=CRITERIA)

NUM_STEPS = 20


for _ in range(NUM_STEPS):
    argument_model.step()
