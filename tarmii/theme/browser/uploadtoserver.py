from cStringIO import StringIO
from DateTime import DateTime
import httplib
import zipfile

from five import grok
from zope.interface import Interface
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.statusmessages.interfaces import IStatusMessage

from tarmii.theme.interfaces import ITARMIIRemoteServerSettings
from tarmii.theme import MessageFactory as _

class UploadToServerView(grok.View):
    """ Create a zip file in memory of the CSV files for logged requests, 
        evaluations sheets and user profiles for the last 30 days and then 
        post the zipfile to the remote url as set up in the configlet.
    """
    grok.context(Interface)
    grok.name('upload-to-server')
    grok.require('zope2.View')

    def zip_csv(self):
        """ Create a zip file in memory of the CSV files for logged requests, 
            evaluations sheets and user profiles for the last 30 days.
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
        if users.user_profiles_csv() is not None:
            zf.writestr('users.csv', users.user_profiles_csv())
        if esheets.evaluation_sheets_csv() is not None:
            zf.writestr('evaluation_sheets.csv',
                        esheets.evaluation_sheets_csv())
        if logs.logged_requests_csv() is not None:
            zf.writestr('logs.csv', logs.logged_requests_csv())
        zf.close()
        in_memory_zip.seek(0)

        return in_memory_zip.read()

    def __call__(self):
        """ Post the zipfile to the remote url as set up in the configlet.
        """

        zip_data = self.zip_csv()
        
        # get settings
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITARMIIRemoteServerSettings)

        # make sure that a server has been specified
        if settings.server_url != None: 
            delimiter_index = settings.server_url.find('/')
            if delimiter_index != -1:
                host = settings.server_url[0:delimiter_index]
                selector = settings.server_url[delimiter_index:]
            else:
                host = settings.server_url[0:]
                selector = ''
        else:
            msg = _('Upload Server not specified in @@remote-server-settings')
            IStatusMessage(self.request).addStatusMessage(msg,"error")
            # redirect to show the error message
            return self.request.response.redirect(
                   '/'.join(self.context.getPhysicalPath()))            

        # send zip data to server
        h = httplib.HTTP(host)
        h.putrequest('POST', selector)
        now = DateTime()
        nice_filename = '%s_%s' % ('tarmii_logs_',now.strftime('%Y%m%d'))
        h.putheader("Content-Disposition", "attachment; filename=%s.zip" % 
                                            nice_filename)
        h.putheader('Content-Type', 'application/octet-stream')
        h.putheader('Content-Length', str(len(zip_data)))
        h.putheader('Last-Modified', DateTime.rfc822(DateTime()))
        h.endheaders()

        body = '\r\n' + zip_data
        h.send(body)
        errcode, errmsg, headers = h.getreply()

        msg = _('File sent to server')
        IStatusMessage(self.request).addStatusMessage(msg,"info")
        # redirect to show the error message
        return self.request.response.redirect(
               '/'.join(self.context.getPhysicalPath()))  


    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''
