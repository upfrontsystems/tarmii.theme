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
                bytes = zf.read(filename)
                users.write(bytes)

        # XXX after unzip is working (above), code from extract_test can be 
        # be filled in below to complete the functionality.

        # extract and grab data
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

        # as a reference from export-user-profiles view:
        #       fieldnames=['username', 'fullname', 'email',
        #                   'teacher_mobile_number', 'school',
        #                   'province', 'EMIS',
        #                   'school_contact_number',
        #                   'school_email', 'qualification',
        #                   'years_teaching','last_login_time',
        #                   'uuid'],

        # sort data by province, school and teacher
        user_data.sort(key= lambda line: ( line.split(",")[5],
                                           line.split(",")[4],
                                           line.split(",")[1]))

        # place data in an organised dictionary
        province_dict = {}
        for user in user_data:
            province_name = user.split(',')[5]

            try:
                x = province_dict[province_name]
                # if this province exists, we do not set it to blank
            except KeyError:
                # province entry did not yet exist, initialise to {}
                province_dict.update({province_name:{}})

            school_dict = province_dict[province_name]
            school_name = user.split(',')[4]

            try:
                x = school_dict[school_name]
                # if this school exists, we do not set it to blank
            except KeyError:
                # school entry did not yet exist, initialise to {}
                school_dict.update({school_name: {}})

            teacher_dict = school_dict[school_name]
            teacher_uuid = user.split(',')[12]
            teacher_data = { 'username' : user.split(',')[0],
                             'fullname' : user.split(',')[1],
                             'email' : user.split(',')[2],
                             'mobile' : user.split(',')[3],
                             'qualification' : user.split(',')[9],
                             'years_teaching' : user.split(',')[10],
                             'last_login_time' : user.split(',')[11],
                           }
            teacher_dict.update({teacher_uuid: teacher_data})

        zf.close()
        return province_dict


    def extract_logs(self):
        zipped_data = self.sitedata.items()
        zipped_file = StringIO()       
        zipped_file.write(zipped_data[0][1][2:]) # [2:] removes leading '\r\n'
        zipped_file.seek(0)
        zf = zipfile.ZipFile(zipped_file, mode='r')
        import pdb; pdb.set_trace()
        logs = StringIO()
        for filename in zf.namelist():
            if filename == 'logs.csv':
                bytes = zf.read(filename)
                logs.write(bytes)

        # XXX after unzip is working (above), code from extract_logs_test can be 
        # be filled in below to complete the functionality.

        # extract and grab the data
        # process and sort

        zf.close()

    def extract_logs_test(self, zipped_data):
        """ """
        # get zip data
        zipped_data.seek(0)
        zf = zipfile.ZipFile(zipped_data, mode='r')
        logs = StringIO()
        for filename in zf.namelist():
            if filename == 'logs.csv':
                bytes = zf.read(filename)
                logs.write(bytes)

        logs.seek(0)
        log_data = logs.getvalue().splitlines()
    
        # as reference from exportloggedrequests
        # fieldnames=['time', 'path', 'username'],

        # place data in an organised dictionary
        log_dict = {}
        datelist = []

        for entry in log_data:
            date_time = entry.split(',')[0]
            date = date_time[:10]

            try:
                x = log_dict[date]
                # if this date exists, we do not set it to blank
            except KeyError:
                # date entry did not yet exist, initialise to {}
                log_dict.update({date:{}})
                datelist.append(date)

            path_data = log_dict[date]
            path_entry = entry.split(',')[1]
            if path_data == {}:
                path_data = []
            path_data.append(path_entry)
            log_dict.update({date: path_data})

        zf.close()
        # log_dict[date] gives us a list of url paths accessed on that date.
        return log_dict, datelist

