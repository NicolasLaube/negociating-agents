"""Comparison class"""


class Comparison:
    """Comparison class.
    This class implements a comparison object used in argument object.

    attr:
        best_criterion_name:
        worst_criterion_name:
    """

    def __init__(self, best_criterion_name, worst_criterion_name):
        """Creates a new comparison."""
        self.__best_criterion_name = best_criterion_name
        self.__worst_criterion_name = worst_criterion_name

    @property
    def best_criterion_name(self):
        """Best criterion name getter"""
        return self.__best_criterion_name

    @property
    def worst_criterion_name(self):
        """Worst criterion name"""
        return self.__worst_criterion_name

    def __str__(self) -> str:
        """Stringyfy Comparison"""
        return (
            f"{self.__worst_criterion_name.name} <= {self.__best_criterion_name.name}"
        )

    def __eq__(self, __o: object) -> bool:
        """Comparison equality"""
        if not isinstance(__o, Comparison):
            return False
        return (
            self.__best_criterion_name == __o.best_criterion_name
            and self.__worst_criterion_name == __o.worst_criterion_name
        )
