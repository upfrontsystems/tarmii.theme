from zope.interface import Interface
from zope.schema import Int, TextLine
from collective.quickupload.interfaces import IQuickUploadCapable

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


class ITARMIIRemoteServerSettings(Interface):
    """ So we can store some settings for the remote server
    """

    server_url = TextLine(
        title=_(u'Remote Server Url'),
        description=_(u'Define the url where the logs can be uploaded.'),
        required=True
    )


class ISiteData(Interface):
    """ A utility used to extract data from a zip file on the request, store it,
        and return sorted contents in a dictionary format
    """


