"""Message class."""
from typing import Union

from communication.arguments.argument import Argument
from communication.message.message_performative import MessagePerformative
from communication.preferences.item import Item


class Message:
    """Message class.
    Class implementing the message object which is exchanged
    between agents through a message service
    during communication.

    attr:
        from_agent: the sender of the message (id)
        to_agent: the receiver of the message (id)
        message_performative: the performative of the message
        content: the content of the message
    """

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_performative: MessagePerformative,
        content: Union[Argument, Item, str],
    ):
        """Create a new message."""
        self.__from_agent = from_agent
        self.__to_agent = to_agent
        self.__message_performative = message_performative
        self.__content = content

    def __str__(self):
        """Return Message as a String."""
        return (
            "From "
            + str(self.__from_agent)
            + " to "
            + str(self.__to_agent)
            + " ("
            + str(self.__message_performative)
            + ") "
            + str(self.__content)
        )

    @property
    def sender(self) -> str:
        """Return the sender of the message."""
        return self.__from_agent

    @property
    def recipient(self):
        """Return the receiver of the message."""
        return self.__to_agent

    @property
    def performative(self):
        """Return the performative of the message."""
        return self.__message_performative

    @property
    def content(self) -> Union[Argument, Item, str]:
        """Return the content of the message."""
        return self.__content
