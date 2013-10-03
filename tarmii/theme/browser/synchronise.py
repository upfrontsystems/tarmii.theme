import os
import logging
import zipfile
import urlparse
import requests

from cStringIO import StringIO
from datetime import datetime
from DateTime import DateTime

from five import grok
from zope.component import getUtility
from zope.interface import Interface
from plone.registry.interfaces import IRegistry
from Products.statusmessages.interfaces import IStatusMessage

from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme.interfaces import ITARMIIRemoteServerSettings
from tarmii.theme import MessageFactory as _


class SynchroniseAssessmentsView(grok.View):
    """ Fetch a file containing all assessment ids from the server.
        Check the ids against the local assessment ids.
        Request a zip file containing all the new assessments and there
        resources (images, etc.) from the same server.
        Open the zip file.
        Add all the new assessments to the local instance.
    """

    grok.context(Interface)
    grok.name('synchronise')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(SynchroniseAssessmentsView, self).__init__(context, request)
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ITARMIIRemoteServerSettings)
        self.xml_content = None

    def update(self):
        import pdb;pdb.set_trace()
        server_url = None
        if self.settings.server_url != None:
            url = self.settings.sync_server_url
            creds = ('admin', 'admin')
            result = requests.get(url, auth=creds)
            self.xml_content = result.text
        else:
            msg = _('Synchronisation server not specified in settings')
            IStatusMessage(self.request).addStatusMessage(msg,"error")
            # redirect to show the error message
            return self.request.response.redirect('/')

    def render(self):
        return self.xml_content

    
