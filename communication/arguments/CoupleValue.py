#!/usr/bin/env python3


class CoupleValue:
    """CoupleValue class.
    This class implements a couple value used in argument object.

    attr:
        criterion_name:
        value:
    """

    def __init__(self, criterion_name, value):
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
