from cStringIO import StringIO
from five import grok
from zope.interface import Interface
from zope.component import getUtility
from plone.directives import dexterity
from Products.CMFCore.utils import getToolByName

from tarmii.theme.interfaces import ISiteData

grok.templatedir('templates')

class Teacher:
    def __init__(self):
        self.data = []

class TeacherProfilesView(grok.View):
    """ View for teacher profiles
    """
    grok.context(Interface)
    grok.name('teacher-profiles')
    grok.template('teacherprofiles')
    grok.require('zope2.View')

    def update(self, **kwargs):

        sitedata = getUtility(ISiteData)

        # display the dictionary nicely
#        self.teacher_data = sitedata.extract_teacher_data()

        # XXX debug - currently calling directly
        view = self.context.restrictedTraverse('@@upload-to-server')
        test_data = StringIO()
        test_data.write(view.zip_csv())
        self.teacher_data = sitedata.extract_test(test_data)
        return

    def show_provinces(self):
        """ show teachers if both province and school are NOT on the request 
        """
        province = bool(self.request.has_key('province'))
        school = bool(self.request.has_key('school'))
        return not province and not school

    def show_schools(self):
        """ show schools if province are on and schools are NOT on the request 
        """
        province = bool(self.request.has_key('province'))
        school = bool(self.request.has_key('school'))
        return province and not school

    def show_teachers(self):
        """ show teachers if both province and school are on the request 
        """
        province = bool(self.request.has_key('province'))
        school = bool(self.request.has_key('school'))
        return province and school

    def context_path(self):
        """ return context url """
        return self.context.absolute_url()

    def province_request(self):
        """ return the province from the request """
        return self.request.get('province')

    def school_request(self):
        """ return the school from the request """
        return self.request.get('school')

    def provinces(self):
        """ return all provinces from teacher_data object
        """
        province_list = []
        for province in range(len(self.teacher_data.items())):
            province_list.append(self.teacher_data.items()[province][0])
        province_list.sort()
        return province_list

    def schools(self):
        """ return all schools in current province from teacher_data object
        """
        school_list = []
        province = self.request.get('province')
        for school in range(len(self.teacher_data[province].items())):
            school_list.append(self.teacher_data[province].items()[school][0])
        school_list.sort()
        return school_list

    def teachers(self):
        """ return all teachers in current school+provinces from teacher_data
            object
        """
        teacher_list = []
        province = self.request.get('province')
        school = self.request.get('school')
        t_data = self.teacher_data[province][school].items()
        for teacher in range(len(t_data)):
            t_obj = Teacher()
            t_obj.EMIS = t_data[teacher][0]
            t_obj.fullname = t_data[teacher][1]['fullname']
            t_obj.username = t_data[teacher][1]['username']
            t_obj.email = t_data[teacher][1]['email']
            t_obj.qualification = t_data[teacher][1]['qualification']
            t_obj.years_teaching = t_data[teacher][1]['years_teaching']
            t_obj.last_login = t_data[teacher][1]['last_login_time']
            teacher_list.append(t_obj)
        return teacher_list

