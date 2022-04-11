"""CoupleValue class."""
from communication.preferences.criterion_name import CriterionName
from communication.preferences.value import Value


class CoupleValue:
    """CoupleValue class.
    This class implements a couple value used in argument object.

    attr:
        criterion_name:
        value:
    """

    def __init__(self, criterion_name: CriterionName, value: Value):
        """Creates a new couple value."""
        self.__criterion_name = criterion_name
        self.__value = value

    @property
    def criterion_name(self):
        """Criterion name"""
        return self.__criterion_name

    @property
    def value(self):
        """Value"""
        return self.__value

    def __str__(self) -> str:
        """String couple value"""
        return f"{self.__criterion_name.name} = {self.__value.name}"

    def __eq__(self, __o: object) -> bool:
        """Couple value equality"""
        if not isinstance(__o, CoupleValue):
            return False

        return self.__criterion_name == __o.criterion_name and self.__value == __o.value
