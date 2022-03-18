from communication.mailbox.Mailbox import Mailbox
from communication.message.Message import Message
from communication import Item
from communication.message.MessagePerformative import MessagePerformative
from communication.pw_argumentation import ArgumentModel

print("Testing two agents communication")


e_car = Item("ElectricCar", "The nice electric car")
diesel_car = Item("DieselCar", "The greate diesel car")

ITEMS = [e_car, diesel_car]
argument_model = ArgumentModel(2, items=ITEMS)

NUM_STEPS = 20


for i in range(NUM_STEPS):
    argument_model.step()
