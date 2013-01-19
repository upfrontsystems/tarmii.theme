from cStringIO import StringIO
from DateTime import DateTime
import zipfile

from five import grok
from zope.interface import Interface
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Products.CMFPlone.utils import getToolByName

from tarmii.theme.interfaces import ITARMIIRemoveServerSettings
from tarmii.theme import MessageFactory as _

class UploadToServerView(grok.View):
    """ Create a zip file in memory of the CSV files for logged requests, 
        evaluations sheets and user profiles for the last 30 days and then 
        post the zipfile to the remote url as set up in the configlet.
    """
    grok.context(Interface)
    grok.name('upload-to-server')
    grok.require('zope2.View')

    def __call__(self):
        """ Create a zip file in memory of the CSV files for logged requests, 
            evaluations sheets and user profiles for the last 30 days and then 
            post the zipfile to the remote url as set up in the configlet.
        """

        # get todays date + date 30 days ago
        start = str(int(DateTime()-30))
        end = str(int(DateTime())) # now

        # fetch data from each view
        users = self.context.restrictedTraverse('@@export-user-profiles')
        self.request.set('start_date',start)
        self.request.set('end_date',end)
        esheets = self.context.restrictedTraverse('@@export-evaluationsheets')
        logs = self.context.restrictedTraverse('@@export-logged-requests')

        # zip data
        in_memory_zip = StringIO()
        zf = zipfile.ZipFile(in_memory_zip, mode='w')
        if users() is not None:
            zf.writestr('users.csv', users())
#        if esheets() is not None:
#            zf.writestr('evaluation_sheets.csv', esheets())
        if logs() is not None:
            zf.writestr('logs.csv', logs())
        zf.close()
        in_memory_zip.seek(0)

        now = DateTime()
        nice_filename = '%s_%s' % ('tarmii_logs_',now.strftime('%Y%m%d'))
        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.zip" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", 'application/octet-stream')
        self.request.response.setHeader("Content-Length", len(in_memory_zip.read()))
        self.request.response.setHeader('Last-Modified',
                                         DateTime.rfc822(DateTime()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")

        in_memory_zip.seek(0)
        self.request.response.write(in_memory_zip.read())

        # send zip data to server 
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITARMIIRemoveServerSettings)
#        print settings.server_url

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''
