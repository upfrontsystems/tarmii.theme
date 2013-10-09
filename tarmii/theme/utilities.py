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

    def store_data(self, data):
        """ Extracted and store the data in OOBTtrees
        """

        # extract csv files from received zip file
        zipped_file = StringIO(data)       
        zf = zipfile.ZipFile(zipped_file, mode='r')
        self.process_users(zf)
        self.process_logs(zf)
        self.process_evaluation_sheets(zf)
        zf.close()

    def process_users(self, zipfile):
        # store user data in persistent storage
        filename = 'users.csv'
        if filename not in zipfile.namelist():
            return

        users = zipfile.read(filename)
        user_data = users.splitlines()

        # as a reference from export-user-profiles view:
        #       fieldnames=['username', 'fullname', 'email',
        #                   'teacher_mobile_number', 'school',
        #                   'province', 'EMIS',
        #                   'school_contact_number',
        #                   'school_email', 'qualification',
        #                   'years_teaching','last_login_time', 'uuid'

        # sort data by province, school and teacher
        user_data.sort(key= lambda line: ( line.split(",")[5],
                                           line.split(",")[4],
                                           line.split(",")[1]))
        # place data in an organised dictionary
        for user in user_data:
            username, fullname, email, mobile, school_name, \
            province_name, EMIS, school_contact_number, school_email, \
            qualification, years_teaching, last_login_time, \
            teacher_uuid = user.split(',')

            if self.user_data.get(province_name) is None:
                # province entry did not yet exist, initialise to {}
                self.user_data.update({province_name:{}})
            school_dict = self.user_data.get(province_name)
            try:
                x = school_dict[school_name]
                # if this school exists, we do not set it to blank
            except KeyError:
                # school entry did not yet exist, initialise to {}
                school_dict.update({school_name: {}})
            teacher_dict = school_dict[school_name]

            try:
                x = teacher_dict[teacher_uuid]
            except KeyError:
                teacher_dict.update({teacher_uuid: {}})
            teacher_data_dict = teacher_dict[teacher_uuid]

            try:
                x = teacher_data_dict['evaluationsheets']
            except KeyError:
                teacher_data_dict.update({'evaluationsheets': {}})
            e_list = teacher_data_dict['evaluationsheets']

            teacher_data = { 'username' : username,
                             'fullname' : fullname,
                             'email' : email,
                             'mobile' : mobile,
                             'qualification' : qualification,
                             'years_teaching' : years_teaching,
                             'last_login_time' : last_login_time,
                             'evaluationsheets' : e_list,
                           }

            teacher_dict.update({teacher_uuid: teacher_data})
            school_dict.update({school_name: teacher_dict})
            self.user_data.update({province_name:school_dict})

    def process_logs(self, zipfile):
        filename = 'logs.csv'
        if filename not in zipfile.namelist():
            return

        logs = zipfile.read(filename)
        log_data = logs.splitlines()

        # as reference from exportloggedrequests
        # fieldnames=['time', 'path', 'username','province','school'],

        # delete all log values that do not contain a province or school
        # entry
        log_data_clean = []
        for entry in range(len(log_data)):
            time, path, username, province_name, school_name = \
            log_data[entry].split(',')
            if province_name != '':
                log_data_clean.append(log_data[entry])
      
        # sort data by province, school and time
        log_data_clean.sort(key= lambda line: ( line.split(",")[3],
                                                line.split(",")[4],
                                                line.split(",")[0]))
        # place data in an organised dictionary
        for entry in range(len(log_data_clean)):
            time, path, username, province_name, school_name = \
            log_data_clean[entry].split(',')
            if self.log_data.get(province_name) is None:
                # province entry did not yet exist, initialise to {}
                self.log_data.update({province_name:{}})
            school_dict = self.log_data.get(province_name)
            try:
                x = school_dict[school_name]
                # if this school exists, we do not set it to blank
            except KeyError:
                # school entry did not yet exist, initialise to {}
                school_dict.update({school_name: {}})
            date_dict = school_dict[school_name]
            date_uuid = time[:10]
            try:
                x = date_dict[date_uuid]
                # if this date exists, we do not set it to blank
            except KeyError:
                # date entry did not yet exist, initialise to {}
                date_dict.update({date_uuid: []})
            date_data = date_dict[date_uuid] # get existing list of
                                             # paths
            # append another path to existing list of paths
            date_data.append(path)

            date_dict.update({date_uuid: date_data})
            school_dict.update({school_name: date_dict})
            self.log_data.update({province_name:school_dict})

    def process_evaluation_sheets(self, zipfile):
        # persistent structure (requires users.csv to have been parsed already)
        filename = 'evaluation_sheets.csv'
        if filename not in zipfile.namelist():
            return

        esheets = zipfile.read(filename)
        esheet_data = esheets.getvalue().splitlines()

        # as a reference from export-evaluationsheets view:
        #               fieldnames=['assessment', 'assessment_date',
        #                           'classlist','learner','learner_uid',
        #                           'activity_number','rating','school',
        #                           'province','uuid','esheet_uid']

        # sort data by uuid, assessment, learner, activity_number
        esheet_data.sort(key= lambda line: ( line.split(",")[9],
                                             line.split(",")[0],
                                             line.split(",")[3],
                                             line.split(",")[5]))

        # place data in the same organised dictionary as user data
        for esheet in esheet_data:

            assessment, assessment_date, classlist, learner, \
            learner_uid, activity_number, rating, school_name, \
            province_name, teacher_uuid, esheet_uid = esheet.split(',')

            school_dict = self.user_data.get(province_name)
            teacher_dict = school_dict[school_name]
            teacher_data_dict = teacher_dict[teacher_uuid]

            try:
                x = teacher_data_dict['evaluationsheets']
            except KeyError:
                teacher_data_dict.update({'evaluationsheets': {}})
            e_list = teacher_data_dict['evaluationsheets']

            evalsheet_key = assessment + '_' + classlist + '_' +\
                esheet_uid
            try:
                x = e_list[evalsheet_key]
            except KeyError:
                e_list.update({evalsheet_key: {}})
            assessment_obj = e_list[evalsheet_key]

            try:
                x = assessment_obj['learners']
            except KeyError:
                assessment_obj.update({'learners': {}})
            l_list = assessment_obj['learners']

            try:
                x = l_list[learner_uid]
            except KeyError:
                l_list.update({learner_uid: {}})
            learner_obj = l_list[learner_uid]
          
            try:
                x = learner_obj['activity_data']
            except KeyError:
                learner_obj.update({'activity_data': []})
            activities = learner_obj['activity_data']

            activity = { 'activity_number' : activity_number,
                         'rating' : rating
                       }
            activities.append(activity)

            learner_obj.update({'activity_data': activities})
            learner_obj.update({'learner_name': learner})
            l_list.update({learner_uid: learner_obj})
            assessment_obj.update({'learners': l_list})
            assessment_obj.update({'assessment_date': assessment_date})
            assessment_obj.update({'assessment': assessment})
            assessment_obj.update({'classlist': classlist})
            e_list.update({evalsheet_key: assessment_obj})
            teacher_data_dict.update({'evaluationsheets': e_list})
            teacher_dict.update({teacher_uuid: teacher_data_dict})
            school_dict.update({school_name: teacher_dict})
            self.user_data.update({province_name:school_dict})
