from cStringIO import StringIO
from DateTime import DateTime
import zipfile
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from zope.component import getUtility
from z3c.form.i18n import MessageFactory as _
from plone.registry.interfaces import IRegistry
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from tarmii.theme.interfaces import ITARMIIRemoteServerSettings
from tarmii.theme.tests.base import TarmiiThemeTestBase

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
