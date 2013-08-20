from csv import DictReader
from cStringIO import StringIO
from DateTime import DateTime
import zipfile

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from zope.interface import implements
from zope.interface import Interface

from tarmii.theme import MessageFactory as _
from tarmii.theme.interfaces import ISiteData

class SiteData(Persistent):
    """ Utility used to store and access site use data/logs
    """
    implements(ISiteData)

    def __init__(self):
        self.user_data = OOBTree()
        self.log_data = OOBTree()
        self.esheet_data = OOBTree()

    def store_data(self, data):
        """ Extracted and store the data in OOBTtrees
        """

        # extract csv files from received zip file
        zipped_file = StringIO()       
        zipped_file.write(data[2:]) # [2:] removes leading '\r\n'
        zipped_file.seek(0)
        zf = zipfile.ZipFile(zipped_file, mode='r')
        users = StringIO()
        logs = StringIO()
        esheets = StringIO()
        for filename in zf.namelist():
            if filename == 'users.csv':
                users.write(zf.read(filename))
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
                for user in user_data:
                    province_name = user.split(',')[5]
                    if self.user_data.get(province_name) is None:
                        # province entry did not yet exist, initialise to {}
                        self.user_data.update({province_name:{}})
                    school_dict = self.user_data.get(province_name)
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

            if filename == 'logs.csv':
                logs.write(zf.read(filename))
                logs.seek(0)
                log_data = logs.getvalue().splitlines()

                # as reference from exportloggedrequests
                # fieldnames=['time', 'path', 'username','province','school'],

                # delete all log values that do not contain a province or school 
                # entry
                log_data_clean = []
                for entry in range(len(log_data)):
                    province_name = log_data[entry].split(',')[3]
                    if province_name != '':
                        log_data_clean.append(log_data[entry])            
              
                # sort data by province, school and time
                log_data_clean.sort(key= lambda line: ( line.split(",")[3],
                                                        line.split(",")[4],
                                                        line.split(",")[0]))
                # place data in an organised dictionary
                for entry in range(len(log_data_clean)):
                    province_name = log_data_clean[entry].split(',')[3]
                    if self.log_data.get(province_name) is None:
                        # province entry did not yet exist, initialise to {}
                        self.log_data.update({province_name:{}})
                    school_dict = self.log_data.get(province_name)
                    school_name = log_data_clean[entry].split(',')[4]
                    try:
                        x = school_dict[school_name]
                        # if this school exists, we do not set it to blank
                    except KeyError:
                        # school entry did not yet exist, initialise to {}
                        school_dict.update({school_name: {}})
                    date_dict = school_dict[school_name]
                    date_uuid = log_data_clean[entry].split(',')[0][:10]
                    try:
                        x = date_dict[date_uuid]
                        # if this date exists, we do not set it to blank
                    except KeyError:
                        # date entry did not yet exist, initialise to {}
                        date_dict.update({date_uuid: []})
                    date_data = date_dict[date_uuid] # get existing list of
                                                     # paths
                    # append another path to existing list of paths
                    date_data.append(log_data_clean[entry].split(',')[1])
                    date_dict.update({date_uuid: date_data})

            if filename == 'evaluation_sheets.csv':
                esheets.write(zf.read(filename))
                esheets.seek(0)
                esheet_data = esheets.getvalue().splitlines()
    
                # XXX
                # We need to figure out how to store evaluationsheet data
                # at the moment it is not being retained

                # as a reference from export-evaluationsheets view:
                #               fieldnames=['assessment', 'assessment_date',
                #                           'class','learner','activity_number',
                #                           'rating'],

        zf.close()
        return
