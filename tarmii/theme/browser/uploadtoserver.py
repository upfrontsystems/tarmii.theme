import base64
import httplib
import logging
import os
import urlparse
import zipfile
from cStringIO import StringIO
from datetime import datetime
from DateTime import DateTime

from five import grok
from zope.interface import Interface
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.statusmessages.interfaces import IStatusMessage

from tarmii.theme.interfaces import ITARMIIRemoteServerSettings
from tarmii.theme import MessageFactory as _

class UploadToServerView(grok.View):
    """ Create a zip file in memory of the CSV files for logged requests, 
        evaluations sheets and user profiles from a specified date
        (stored in ITARMIIRemoteServerSettings registry) until the current date
        and then post the zipfile to the remote url as set up in the configlet.
    """

    grok.context(Interface)
    grok.name('upload-to-server')
    grok.require('cmf.ManagePortal')

    def zip_csv(self):
        """ Create a zip file in memory of the CSV files for logged requests, 
            evaluations sheets and user profiles from a specified date
            (stored in ITARMIIRemoteServerSettings registry) until the current
        """

        # get settings
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITARMIIRemoteServerSettings)
        # make sure that a last successful upload has been specified before
        if settings.last_successful_upload != None:
            # set selection start date as the last successful upload date
            start = DateTime(settings.last_successful_upload)
            end = str(int(DateTime())) # now
        else:
            start = DateTime('2013-01-01 00:00:00') # earliest 'possible' date
            end = str(int(DateTime())) # now

        # fetch data from each view
        users = self.context.restrictedTraverse('@@export-user-profiles')
        self.request.set('start_date', start)
        self.request.set('end_date', end)
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
            parts = urlparse.urlparse(settings.server_url)
        else:
            msg = _('Upload Server not specified in settings')
            IStatusMessage(self.request).addStatusMessage(msg,"error")
            # redirect to show the error message
            return self.request.response.redirect(
                   '/'.join(self.context.getPhysicalPath()))

        # send zip data to server
        h = httplib.HTTP(parts.netloc) # ignore leading '//'
        h.putrequest('POST', parts.path)
        now = DateTime()
        body = '\r\n' + zip_data

        memberid = os.environ['TEACHERDATA_USER']
        passwd = os.environ['TEACHERDATA_PASS']
        authstr = "%s:%s" % (memberid, passwd)

        nice_filename = '%s_%s' % ('tarmii_logs_', now.strftime('%Y%m%d'))
        h.putheader('Authorization', 'Basic ' + base64.b64encode(authstr))
        h.putheader("Content-Disposition", "attachment; filename=%s.zip" % 
                                            nice_filename)
        h.putheader('Content-Type', 'application/octet-stream')
        h.putheader('Content-Length', str(len(body)))
        h.putheader('Last-Modified', DateTime.rfc822(DateTime()))
        h.endheaders()

        h.send(body)
        errcode, errmsg, headers = h.getreply()

        if errcode == 200:
            # if upload successful, set date in registry
            dt = DateTime().asdatetime().replace(tzinfo=None)
            settings.last_successful_upload = \
                datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
            msg = str(errcode) + ' : ' +_('File sent to server')
            IStatusMessage(self.request).addStatusMessage(msg,"info")
        else:
            msg = str(errcode) + ' : ' + _('File not sent successfully')
            IStatusMessage(self.request).addStatusMessage(msg,"error")            
            log = logging.getLogger('tarmii.theme.uploadtoserver')
            log.error(msg)

        # redirect to show the error message
        return self.request.response.redirect(
               '/'.join(self.context.getPhysicalPath()))  

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''
