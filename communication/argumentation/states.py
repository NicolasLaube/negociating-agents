"""Negociation states."""
from enum import Enum


class NegotationState(Enum):
    """NegotationState enum class.
    Enumeration containing the possible agent negotiation states.
    """

    REST = 0
    ARGUING = 1
    WAITING_ANSWER_ACCEPT = 2
    WAITING_FOR_COMMIT = 3
    FINISHED = 4
