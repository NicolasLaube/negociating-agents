"""Preferences"""


import random
from typing import List

from communication.preferences.criterion_name import CriterionName
from communication.preferences.criterion_value import CriterionValue
from communication.preferences.item import Item
from communication.preferences.value import Value


class Preferences:
    """Preferences class.
    This class implements the preferences of an agent.

    attr:
        criterion_name_list: the list of criterion name (ordered by importance)
        criterion_value_list: the list of criterion value
    """

    def __init__(self):
        """Creates a new Preferences object."""
        self.__criterion_name_list: List[CriterionName] = []
        self.__criterion_value_list: List[CriterionValue] = []

    def __str__(self):
        """Returns a string representation of the preferences."""
        return (
            "Preferences:\n"
            + "Criterion names: "
            + str(
                [str(criterion_name) for criterion_name in self.__criterion_name_list]
            )
            + "\n"
            + "Criterion values: "
            + str(
                [
                    str(criterion_value)
                    for criterion_value in self.__criterion_value_list
                ]
            )
            + "\n"
        )

    # @property
    # def criterion_name_list(self):
    #     return self.__criterion_name_list

    def get_criterion_name_list(self) -> List[CriterionName]:
        """Returns the list of criterion name."""
        return self.__criterion_name_list

    def get_criterion_value_list(self) -> List[CriterionValue]:
        """Returns the list of criterion value."""
        return self.__criterion_value_list

    def set_criterion_name_list(self, criterion_name_list: List[CriterionName]) -> None:
        """Sets the list of criterion name."""
        self.__criterion_name_list = criterion_name_list

    def add_criterion_value(self, criterion_value: CriterionValue) -> None:
        """Adds a criterion value in the list."""
        self.__criterion_value_list.append(criterion_value)

    def get_value(self, item: Item, criterion_name: CriterionName) -> Value:
        """Gets the value for a given item and a given criterion name."""
        for criterion_value in self.__criterion_value_list:
            if (
                criterion_value.item.name == item.name
                and criterion_value.get_criterion_name() == criterion_name
            ):
                return criterion_value.value
        raise ValueError("The criterion_name is not in the list of criterion values.")

    def is_preferred_criterion(
        self, criterion_name_1: CriterionName, criterion_name_2: CriterionName
    ) -> bool:
        """Returns if a criterion 1 is preferred to the criterion 2."""
        for criterion_name in self.__criterion_name_list:
            if criterion_name == criterion_name_1:
                return True
            if criterion_name == criterion_name_2:
                return False
        return False

    def is_preferred_item(self, item_1: Item, item_2: Item) -> bool:
        """Returns if the item 1 is preferred to the item 2."""
        return bool(item_1.get_score(self) > item_2.get_score(self))

    def most_preferred(self, item_list: List[Item]) -> Item:
        """Returns the most preferred item from a list."""
        sorted_item_list: List[Item] = sorted(
            item_list, key=lambda item: item.get_score(self), reverse=True  # type: ignore
        )
        if len(sorted_item_list) > 1 and sorted_item_list[0].get_score(
            self
        ) == sorted_item_list[1].get_score(self):
            return random.choice([sorted_item_list[0], sorted_item_list[1]])
        return sorted_item_list[0]

    def is_item_among_top_percent(
        self, item: Item, item_list: List[Item], percentage: int = 20
    ) -> bool:
        """
        Return whether a given item is among the top 10 percent of the preferred items.

        :return: a boolean, True means that the item is among the favourite ones
        """
        proportion = percentage / 100
        sorted_item_list = sorted(
            item_list,
            key=lambda item: item.get_score(self),  # type: ignore
            reverse=True,
        )
        return (
            item in sorted_item_list[: max(1, int(len(sorted_item_list) * proportion))]
        )

    def set_criterion_pair(
        self, less_preferred: CriterionName, more_preferred: CriterionName
    ) -> None:
        """To set a criterion pair."""
        i_less, i_more = -1, -1
        for i, criterion in enumerate(self.__criterion_name_list):
            if criterion == less_preferred:
                i_less = i
            if criterion == more_preferred:
                i_most = i
        if i_less == -1 or i_most == -1:
            raise Exception("The criterion pair is not in the list of criterion names.")
        if i_less < i_most:
            self.__criterion_name_list[i_less], self.__criterion_name_list[i_more] = (
                self.__criterion_name_list[i_more],
                self.__criterion_name_list[i_less],
            )

    def set_criterion_value(
        self, item: Item, criterion_name: CriterionName, item_value: Value
    ) -> None:
        """To set a criterion value."""
        for criterion_value in self.__criterion_value_list:
            if (
                criterion_value.item.name == item.name
                and criterion_value.get_criterion_name() == criterion_name
            ):
                criterion_value.value = item_value


if __name__ == "__main__":
    agent_pref = Preferences()
    agent_pref.set_criterion_name_list(
        [
            CriterionName.PRODUCTION_COST,
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.CONSUMPTION,
            CriterionName.DURABILITY,
            CriterionName.NOISE,
        ]
    )

    diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.PRODUCTION_COST, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.CONSUMPTION, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.DURABILITY, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.NOISE, Value.VERY_BAD)
    )

    electric_engine = Item("Electric Engine", "A very quiet engine")
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.PRODUCTION_COST, Value.BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.CONSUMPTION, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.DURABILITY, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(
            electric_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD
        )
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.NOISE, Value.VERY_GOOD)
    )

    # test list of preferences
    print(diesel_engine)
    print(electric_engine)
    print(diesel_engine.get_value(agent_pref, CriterionName.PRODUCTION_COST))
    print(
        agent_pref.is_preferred_criterion(
            CriterionName.CONSUMPTION, CriterionName.NOISE
        )
    )
    print(
        f"""Electric Engine > Diesel Engine : {agent_pref.is_preferred_item(
            electric_engine, diesel_engine
        )}"""
    )
    print(
        f"""Diesel Engine > Electric Engine : {agent_pref.is_preferred_item(
            diesel_engine, electric_engine
        )}"""
    )
    print(f"Electric Engine (for agent 1) = {electric_engine.get_score(agent_pref)}")
    print(f"Diesel Engine (for agent 1) = {diesel_engine.get_score(agent_pref)}")
    print(
        f"""Most preferred item is : {agent_pref.most_preferred(
            [diesel_engine, electric_engine]).name
        }"""
    )
