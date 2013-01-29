from csv import DictReader
from cStringIO import StringIO
from DateTime import DateTime
import zipfile

from persistent import Persistent
from BTrees.IOBTree import IOBTree
from zope.interface import implements
from zope.interface import Interface

from tarmii.theme import MessageFactory as _
from tarmii.theme.interfaces import ISiteData

class SiteData(Persistent):
    """ Utility used to store and access site use data/logs
    """
    implements(ISiteData)

    def __init__(self):
        self.sitedata = IOBTree()

    def store_data(self, data):
        """ Store the zipped up data in an IOBTtree
        """
        self.sitedata.clear() # remove old data
        self.sitedata[0] = data


