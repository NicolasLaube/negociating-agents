"""Generator of preferences"""
from typing import List
import csv
import random

from communication.preferences.preferences import Preferences
from communication.preferences.criterion_name import CriterionName
from communication.preferences.criterion_value import CriterionValue
from communication.preferences.item import Item
from communication.preferences.value import Value


def load_preferences(path: str) -> Preferences:
    """Load preferences from csv"""
    preferences = Preferences()
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        categories = next(reader)
        preferences.set_criterion_name_list([CriterionName(x) for x in categories[1:]])
        # print("criterion name list ", preferences.criterion_name_list)
        items = []
        for row in reader:
            new_item = Item(row[0], f"This is a {row[0]}")
            items.append(new_item)
            for i, criterion_name in enumerate(categories[1:]):
                criterion_value = CriterionValue(
                    new_item, CriterionName(criterion_name), Value(int(row[i + 1]))
                )
                preferences.add_criterion_value(criterion_value)
    return preferences


def generate_random_preferences(items: List[Item], criteria: List[CriterionName]):
    """Generate preferences"""
    preferences = Preferences()
    random.shuffle(criteria)
    preferences.set_criterion_name_list(criteria)
    for item in items:
        for criterion in criteria:
            preferences.add_criterion_value(
                CriterionValue(item, criterion, random.choice(list(Value)))
            )
    return preferences
