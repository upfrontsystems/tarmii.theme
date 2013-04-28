from z3c.form.i18n import MessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestExportActivitiesView(TarmiiThemeTestBase):
    """ Test ExportActivitiesView view """

    def test_all_activities_csv(self):

        view = self.portal.restrictedTraverse('@@export-activities')
        test_out = view.all_activities_csv()

        csv_ref = 'assessmentitem1,Afrikaans,Grade 1,,Mathematics\r\n' +\
                  'assessmentitem2,,Grade 1,,Mathematics\r\n' +\
                  'assessmentitem3,,,,\r\n' +\
                  'assessmentitem4,,,,\r\n'

        self.assertEqual(test_out,csv_ref)

    def test__call__(self):

        view = self.portal.restrictedTraverse('@@export-activities')
        test_out = view()
        
        csv_ref = 'assessmentitem1,Afrikaans,Grade 1,,Mathematics\r\n' +\
                  'assessmentitem2,,Grade 1,,Mathematics\r\n' +\
                  'assessmentitem3,,,,\r\n' +\
                  'assessmentitem4,,,,\r\n'

        self.assertEqual(test_out,csv_ref)
        ct = self.request.response.getHeader("Content-Type")
        self.assertEqual(ct,"text/csv")
