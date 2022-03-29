"""Argument class."""
from typing import List

from communication.arguments.comparison import Comparison
from communication.arguments.couple_value import CoupleValue
from communication.preferences import Item, Preferences, Value


class Argument:
    """Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision:s
        item:
        comparison_list:
        couple_values_list:
    """

    def __init__(self, boolean_decision: bool, item: Item):
        """Creates a new Argument."""
        self.__decision = boolean_decision
        self.__item: Item = item
        self.__comparison_list: List[Comparison] = []
        self.__couple_values_list: List[CoupleValue] = []

    @property
    def decision(self):
        """Decision"""
        return self.__decision

    @property
    def item(self):
        """Item"""
        return self.__item

    def add_premiss_comparison(self, comparison):
        """Adds a premiss comparison in the comparison list."""
        self.__comparison_list.append(comparison)

    def add_premiss_couple_values(self, couple_value):
        """Add a premiss couple values in the couple values list."""
        self.__couple_values_list.append(couple_value)

    def __str__(self) -> str:
        return (
            f"{'¬' if not self.__decision else ''}{self.__item.get_name()} ← "
            + ", ".join(map(str, self.__couple_values_list))
            + (
                ", "
                if len(self.__couple_values_list) > 0
                and len(self.__comparison_list) > 0
                else ""
            )
            + ", ".join(map(str, self.__comparison_list))
        )

    def get_item(self) -> Item:
        """To get the item"""
        return self.__item

    def get_decision(self) -> bool:
        """To get the decision"""
        return self.__decision

    def get_premises_comparison(self) -> List[Comparison]:
        """To get the premises comparions"""
        return self.__comparison_list

    def get_premises_couple_values(self) -> List[CoupleValue]:
        """To get the premises couple values"""
        return self.__couple_values_list

    @staticmethod
    def list_supporting_proposal(item: Item, preferences: Preferences):
        """Generate a list of premisses which can be used to support an item
        :param item: Item - name of the item
        :return: list of all premisses PRO an item (sorted by order of importance
        based on agent’s preferences)"""
        return sorted(
            [
                CoupleValue(criterion, preferences.get_value(item, criterion))
                for criterion in preferences.get_criterion_name_list()
                if preferences.get_value(item, criterion).value >= Value.GOOD.value
            ],
            key=lambda cv: cv.value.value,  # type: ignore
            reverse=True,
        )

    @staticmethod
    def list_attacking_proposal(item: Item, preferences: Preferences):
        """List attacking proposal"""
        return sorted(
            [
                CoupleValue(criterion, preferences.get_value(item, criterion))
                for criterion in preferences.get_criterion_name_list()
                if preferences.get_value(item, criterion).value < Value.GOOD.value
            ],
            key=lambda cv: cv.value.value,  # type: ignore
            reverse=True,
        )
