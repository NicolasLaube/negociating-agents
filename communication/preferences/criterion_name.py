"""Criterion Name"""
from enum import Enum


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

    @staticmethod
    def list_presidential():
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
    def list_cars():
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
