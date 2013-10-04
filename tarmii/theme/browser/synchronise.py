import os
import lxml
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
from Products.CMFCore.utils import getToolByName
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
        self.ids_xml = None

    def update(self):
        if self.settings.sync_server_url is None or \
           self.settings.sync_server_user is None or \
           self.settings.sync_server_password is None:

            msg = _('Synchronisation server settings are incomplete.')
            IStatusMessage(self.request).addStatusMessage(msg,"error")
            # redirect to show the error message
            return self.request.response.redirect('/')
        
        self.ids_xml = self.fetch_ids(self.settings)
        self.missing_ids = self.missing_ids(self.ids_xml)

    def fetch_ids(self, settings):
        url = settings.sync_server_url + '/@@assessmentitem-ids-xml'
        user = settings.sync_server_user
        password = settings.sync_server_password
        creds = (user, password)
        result = requests.get(url, auth=creds)
        return result.text

    def missing_ids(self, ids_xml):
        import pdb;pdb.set_trace()
        new_ids_tree = lxml.etree.fromstring(ids_xml)
        new_ids = [e.get('id') for e in new_ids_tree.findall('assessmentitem')]

        pc = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type': 'upfront.assessmentitem.content.assessmentitem'}
        brains = pc(query)

        # if we have no assessment items, don't bother comparing, just return
        if len(brains) < 1:
            return new_ids

        current_ids = [brain.getId for brain in brains]
        return set(new_ids).difference(current_ids)

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/xml')
        return self.ids_xml

    
