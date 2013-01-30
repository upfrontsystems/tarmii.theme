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

    def extract_teacher_data(self):
        zipped_data = self.sitedata.items()
        zipped_file = StringIO()       
        zipped_file.write(zipped_data[0][1][2:]) # [2:] removes leading '\r\n'
        zipped_file.seek(0)
        zf = zipfile.ZipFile(zipped_file, mode='r')
        import pdb; pdb.set_trace()
        users = StringIO()
        for filename in zf.namelist():
            if filename == 'users.csv':
                print filename
                bytes = zf.read(filename)
                print len(bytes)
                users.write(bytes)

        # extract and grab the users


        # process and sort

        zf.close()



