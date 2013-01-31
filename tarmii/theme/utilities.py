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

    def extract_test(self, zipped_data):
        """ """
        # get zip data
        zipped_data.seek(0)
        zf = zipfile.ZipFile(zipped_data, mode='r')
        users = StringIO()
        for filename in zf.namelist():
            if filename == 'users.csv':
                bytes = zf.read(filename)
                users.write(bytes)

        users.seek(0)
        user_data = users.getvalue().splitlines()

        # sort data by province, school and teacher
        user_data.sort(key= lambda line: ( line.split(",")[4],
                                           line.split(",")[3],
                                           line.split(",")[1]))

        # place data in an organised dictionary
        province_dict = {}
        for user in user_data:
            province_name = user.split(',')[4]

            try:
                x = province_dict[province_name]
                # if this province exists, we do not set it to blank
            except KeyError:
                # province entry did not yet exist, initialise to {}
                province_dict.update({province_name:{}})

            school_dict = province_dict[province_name]
            school_name = user.split(',')[3]

            try:
                x = school_dict[school_name]
                # if this school exists, we do not set it to blank
            except KeyError:
                # school entry did not yet exist, initialise to {}
                school_dict.update({school_name: {}})

            teacher_dict = school_dict[school_name]
            teacher_EMIS = user.split(',')[5]
            teacher_data = { 'username' : user.split(',')[0],
                             'fullname' : user.split(',')[1],
                             'email' : user.split(',')[2], 
                             'qualification' : user.split(',')[8],
                             'years_teaching' : user.split(',')[9],
                             'last_login_time' : user.split(',')[10],
                           }
            teacher_dict.update({teacher_EMIS: teacher_data})

        zf.close()
        return province_dict

