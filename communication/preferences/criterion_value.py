"""Criterion value"""


from communication.preferences.criterion_name import CriterionName
from communication.preferences.item import Item
from communication.preferences.value import Value


class CriterionValue:
    """CriterionValue class.
    This class implements the CriterionValue object which associates
    an item with a CriterionName and a Value.
    """

    def __init__(self, item: Item, criterion_name: CriterionName, value: Value):
        """Creates a new CriterionValue."""
        self.__item = item
        self.__criterion_name = criterion_name
        self.__value = value

    def __str__(self) -> str:
        """Returns a string representation of the criterion value."""
        return (
            "Criterion value:\n"
            + "Item: "
            + str(self.__item)
            + "\n"
            + "Criterion name: "
            + str(self.__criterion_name)
            + "\n"
            + "Value: "
            + str(self.__value)
            + "\n"
        )

    @property
    def item(self) -> Item:
        """Returns the item."""
        return self.__item

    def get_criterion_name(self) -> CriterionName:
        """Returns the criterion name."""
        return self.__criterion_name

    @property
    def value(self) -> Value:
        """Returns the value."""
        return self.__value

    @value.setter
    def value(self, value) -> None:
        """Sets the value."""
        self.__value = value
