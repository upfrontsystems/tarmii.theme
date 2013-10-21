from zope.interface import Interface
from zope.schema import Int, TextLine, Datetime
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
        description=_(u'Define the url where the logs can be uploaded'),
        required=True
    )

    upload_server_user = TextLine(
        title=_(u'Data upload user name'),
        description=_(u'Used to log in to the server.'),
        required=True
    )

    upload_server_password = TextLine(
        title=_(u'Upload password'),
        description=_(u'Used to log in to the server.'),
        required=True
    )

    last_successful_upload = Datetime(
        title=_(u'Last Successful Upload Date'),
        description=_(u'Stores last date of successful data upload'),
        required=False
    )

    sync_server_url = TextLine(
        title=_(u'Synchronisation Server Url'),
        description=_(u'Fetch the latests assessment items from this server.'),
        required=True
    )

    sync_server_user = TextLine(
        title=_(u'Synchronisation Server user name'),
        description=_(u'Used to log in to the synchronisation server.'),
        required=True
    )

    sync_server_password = TextLine(
        title=_(u'Synchronisation Server password'),
        description=_(u'Used to log in to the synchronisation server.'),
        required=True
    )


class ISiteData(Interface):
    """ A utility used to extract data from a zip file on the request, store it,
        and return sorted contents in a dictionary format
    """


