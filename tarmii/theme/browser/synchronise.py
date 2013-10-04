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
        self.url = self.settings.sync_server_url
        self.user = self.settings.sync_server_user
        self.password = self.settings.sync_server_password
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
        missing_ids = self.missing_ids(self.ids_xml)
        assessments_xml = self.fetch_assessments(missing_ids)

    def fetch_ids(self, settings):
        ids_url = self.url + '/@@assessmentitem-ids-xml'
        creds = (self.user, self.password)
        result = requests.get(ids_url, auth=creds)
        return result.text

    def missing_ids(self, ids_xml):
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

    def fetch_assessments(self, missing_ids):
        assessments_url = self.url + '/@@assessmentitem-xml'
        tree = lxml.etree.fromstring('<xml/>')
        for a_id in missing_ids:
            element = lxml.etree.Element('assessmentitem')
            element.set('id', a_id)
            element.text = 'Assessment item %s' % a_id
            tree.append(element)
        xml = lxml.etree.tostring(tree)
        creds = (self.user, self.password)
        requests.post(assessments_url, data={'xml':xml}, auth=creds)

    def render(self):
        response = self.request.response
        response.setHeader('Content-type', 'text/xml')
        response.setHeader('expires', 0)
        response['Content-Length'] = len(self.ids_xml)
        response.write(self.ids_xml)
