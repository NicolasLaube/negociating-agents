from communication import Item
from communication.preferences.CriterionName import CriterionName
from communication.pw_argumentation import ArgumentModel

print("Testing two agents communication")


e_car = Item("ElectricCar", "The nice electric car")
diesel_car = Item("DieselCar", "The greate diesel car")

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
