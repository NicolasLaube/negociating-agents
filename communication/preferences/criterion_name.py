"""Criterion Name"""
from __future__ import annotations

from enum import Enum
from typing import List

# class CriterionNameCars(Enum):
#     """CriterionName enum class.
#     Enumeration containing the possible CriterionName for cars.
#     """

#     PRODUCTION_COST = "production_cost"
#     CONSUMPTION = "consumption"
#     DURABILITY = "durability"
#     ENVIRONMENT_IMPACT = "environment_impact"
#     NOISE = "noise"

#     @staticmethod
#     def list():
#         return list(map(lambda c: c, CriterionNameCars))


class CriterionName(Enum):
    """CriterionName enum class.
    Enumeration containing the possible CriterionName for presidents.
    """

    EDUCATION = "education"
    LIBERALISM = "liberalism"
    IMMIGRATION = "immigration"
    ENVIRONMENT = "environment"
    SECURITY = "security"
    WORK = "work"

    PRODUCTION_COST = "production_cost"
    CONSUMPTION = "consumption"
    DURABILITY = "durability"
    ENVIRONMENT_IMPACT = "environment_impact"
    NOISE = "noise"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def list_presidential() -> List[CriterionName]:
        """Return the list of presidential CriterionName."""
        return [
            c
            for c in CriterionName
            if c.name
            in [
                "EDUCATION",
                "LIBERALISM",
                "IMMIGRATION",
                "ENVIRONMENT",
                "SECURITY",
                "WORK",
            ]
        ]

    @staticmethod
    def list_cars() -> List[CriterionName]:
        """Return the list of the cars CriterionName"""
        return [
            c
            for c in CriterionName
            if c.name
            in [
                "PRODUCTION_COST",
                "CONSUMPTION",
                "DURABILITY",
                "ENVIRONMENT_IMPACT",
                "NOISE",
            ]
        ]
