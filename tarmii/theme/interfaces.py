from zope.interface import Interface
from zope.schema import Int

from tarmii.theme import MessageFactory as _

class ITARMIIThemeLayer(Interface):
    """ Marker interface for tarmii.theme """

class ILastItemVersionNumber(Interface):
    """ Last assessment item version number
    """
    version = Int(
        title=_('Last version number'),
        required=True,
        default=0
    )


class IItemVersion(Interface):
    """ Interface for ItemVersion utility
    """

    def next_version():
        """ Return the next version number for an assessment item
        """
