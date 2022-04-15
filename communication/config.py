import os

from communication.preferences.item import Item

# PERCENTAGES OF PREFERENCES
INITIAL_PERCENTAGE = 10
INCREASE_PERCENTAGE = 20

CAR_ITEMS = [
    Item("E", "The nice electric car"),
    Item("ICED", "The great diesel car"),
    Item("HYBRID", "The super hybrid car"),
]

PRESIDENTIAL_ITEMS = [
    Item("MANIOC", "Center"),
    Item("MELON", "Far-Left"),
    Item("ZEBRA", "Far-Right"),
    Item("JASMIN", "Left"),
    Item("PECANS", "Right"),
]

ITEM_COLORS = {
    "MELON": "red",
    "JASMIN": "green",
    "MANIOC": "purple",
    "PECANS": "cornflowerblue",
    "ZEBRA": "navy",
    "ICED": "red",
    "HYBRID": "yellow",
    "E": "green",
}

CARS_PREFERENCES_FOLDER = os.path.join("data", "preferences", "cars")
PRESIDENTIAL_PREFERENCES_FOLDER = os.path.join("data", "preferences", "presidential")

MAX_NUM_STEPS = 100
