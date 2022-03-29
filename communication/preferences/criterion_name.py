"""Criterion Name"""
from enum import Enum


class CriterionName(Enum):
    """CriterionName enum class.
    Enumeration containing the possible CriterionName.
    """

    PRODUCTION_COST = "production_cost"
    CONSUMPTION = "consumption"
    DURABILITY = "durability"
    ENVIRONMENT_IMPACT = "environment_impact"
    NOISE = "noise"
