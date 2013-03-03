from z3c.form.i18n import MessageFactory as _
from plone.app.controlpanel.security import ISecuritySchema
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestExportUserProfilesView(TarmiiThemeTestBase):
    """ Test ExportUserProfilesView view """

    def test__user_profiles_csv(self):

        #create user
        username = 'testuser2'
        passwd = username
        title = 'Test User2'
        properties = {'username' : username,
                      'fullname' : title.encode("utf-8"),
                      'email' : 'testuser2@email.com',   
                      'teacher_mobile_number': '0821111222',
                      'school': 'CoolSchool',
                      'province': 'WC',
                      'EMIS': '12345',
                      'school_contact_number': '1111',
                      'school_email': 'coolschool@schools.com',
                      'qualification': 'Teacher',
                      'years_teaching': '2',
                      'uuid' : 'qwerty-001',
                     }                       

        security_adapter =  ISecuritySchema(self.portal)
        # enable self-registration of users
        security_adapter.set_enable_self_reg(True)

        regtool = getToolByName(self.portal, 'portal_registration')
        member = regtool.addMember(username, passwd, properties=properties)

        pm = self.portal.portal_membership
        acl = self.portal.acl_users
        acl.session._setupSession(username,self.request.RESPONSE)

        view = self.portal.restrictedTraverse('@@export-user-profiles')
        test_out = view.user_profiles_csv()

        csv_ref = 'test_user_1_,,,,,,,,,,,01/01/2000 00:00:00,\r\n' +\
                  'testuser2,Test User2,testuser2@email.com,0821111222,' +\
                  'CoolSchool,WC,12345,1111,coolschool@schools.com,Teacher,' +\
                  '2,01/01/2000 00:00:00,qwerty-001\r\n'

        self.assertEqual(test_out,csv_ref)

    def test__call__(self):

        #create user
        username = 'testuser2'
        passwd = username
        title = 'Test User2'
        properties = {'username' : username,
                      'fullname' : title.encode("utf-8"),
                      'email' : 'testuser2@email.com',   
                      'teacher_mobile_number': '0821111222',
                      'school': 'CoolSchool',
                      'province': 'WC',
                      'EMIS': '12345',
                      'school_contact_number': '1111',
                      'school_email': 'coolschool@schools.com',
                      'qualification': 'Teacher',
                      'years_teaching': '2',
                      'uuid' : 'qwerty-001',
                     }                       

        security_adapter =  ISecuritySchema(self.portal)
        # enable self-registration of users
        security_adapter.set_enable_self_reg(True)

        regtool = getToolByName(self.portal, 'portal_registration')
        member = regtool.addMember(username, passwd, properties=properties)

        pm = self.portal.portal_membership
        acl = self.portal.acl_users
        acl.session._setupSession(username,self.request.RESPONSE)

        view = self.portal.restrictedTraverse('@@export-user-profiles')
        test_out = view()

        csv_ref = 'test_user_1_,,,,,,,,,,,01/01/2000 00:00:00,\r\n' +\
                  'testuser2,Test User2,testuser2@email.com,0821111222,' +\
                  'CoolSchool,WC,12345,1111,coolschool@schools.com,Teacher,' +\
                  '2,01/01/2000 00:00:00,qwerty-001\r\n'

        self.assertEqual(test_out,csv_ref)
        ct = self.request.response.getHeader("Content-Type")
        self.assertEqual(ct,"text/csv")

