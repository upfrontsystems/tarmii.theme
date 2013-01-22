from cStringIO import StringIO
from DateTime import DateTime
import zipfile
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from z3c.form.i18n import MessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from tarmii.theme.tests.base import TarmiiThemeTestBase

from upfront.pagetracker.interfaces import IPageTracker
from upfront.pagetracker.tests.base import UpfrontPageTrackerTestBase

class TestUploadToServerView(TarmiiThemeTestBase):
    """ Test UploadToServer view """

    def test_zip_csv(self):

        # prepare the zip contents
        # users csv will exist because there is one user in the system
        users = self.portal.restrictedTraverse('@@export-user-profiles')
        # zip data
        in_memory_zip = StringIO()
        zf = zipfile.ZipFile(in_memory_zip, mode='w')
        zf.writestr('users.csv', users.user_profiles_csv())
        zf.close()
        in_memory_zip.seek(0)

        view = self.portal.restrictedTraverse('@@upload-to-server')
        test_out = view.zip_csv()
        self.assertEqual(test_out,in_memory_zip.read())

    def test__call__(self):

        # prepare the zip contents
        # users csv will exist because there is one user in the system
        users = self.portal.restrictedTraverse('@@export-user-profiles')
        # zip data
        in_memory_zip = StringIO()
        zf = zipfile.ZipFile(in_memory_zip, mode='w')
        zf.writestr('users.csv', users.user_profiles_csv())
        zf.close()
        in_memory_zip.seek(0)
        test_zip_data = in_memory_zip.read()

        view = self.portal.restrictedTraverse('@@upload-to-server')
        self.request.RESPONSE.stdout = StringIO()
        view()
        self.request.RESPONSE.stdout.seek(0)

        now = DateTime()
        filename = '%s_%s' % ('tarmii_logs_',now.strftime('%Y%m%d'))
        date_time = DateTime.rfc822(DateTime())

        csv_ref = 'Status: 200 OK\r\n' +\
                  'X-Powered-By: Zope (www.zope.org), ' +\
                  'Python (www.python.org)\r\n' +\
                  'Content-Length: 159\r\n' +\
                  'Content-Disposition: attachment; filename=' +\
                   filename + '.zip\r\n' +\
                  'Last-Modified: ' + date_time +'\r\n' +\
                  'Pragma: no-cache\r\n' +\
                  'Cache-Control: no-store\r\n' +\
                  'Content-Type: application/octet-stream\r\n' +\
                  '\r\n' + test_zip_data

        self.request.RESPONSE.stdout.seek(0)
        self.assertEqual(self.request.RESPONSE.stdout.read(),csv_ref) 
 


