import os
import lxml
import logging
import urlparse
import requests
from zipfile import ZipFile
from cStringIO import StringIO

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


grok.templatedir('templates')

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
    grok.template('synchronise')

    def __init__(self, context, request):
        super(SynchroniseAssessmentsView, self).__init__(context, request)
        self.portal = self.context.restrictedTraverse(
            'plone_portal_state').portal()
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ITARMIIRemoteServerSettings)
        self.url = self.settings.sync_server_url
        self.user = self.settings.sync_server_user
        self.password = self.settings.sync_server_password
        self.ids_xml = None
        self.assessments_zip = None

    def update(self):
        if self.settings.sync_server_url is None or \
           self.settings.sync_server_user is None or \
           self.settings.sync_server_password is None:
            error = 'Synchronisation server settings are incomplete.'
            self.add_errors([error])
         
        errors, self.ids_xml = self.fetch_ids(self.settings)
        if errors:  
            self.add_errors(errors)
            return

        missing_ids = self.missing_ids(self.ids_xml)
        if not missing_ids:
            msg = 'Assessment items up to date.'
            self.add_messages([msg])
            return

        errors, assessments_zip = self.fetch_assessments_zip(missing_ids)
        if errors:
            self.add_errors(errors)
            return

        errors, imported = self.import_assessments(assessments_zip)
        if errors:
            self.add_errors(errors)
            return
        self.add_messages(imported)

    def fetch_ids(self, settings):
        ids_url = self.url + '/@@assessmentitem-ids-xml'
        creds = (self.user, self.password)
        try:
            result = requests.get(ids_url, auth=creds)
            return None, result.content
        except ConnectionError:
            return 'Could not connect to %s.' % ids_url, None

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

    def fetch_assessments_zip(self, missing_ids):
        assessments_url = self.url + '/@@assessmentitem-xml'
        tree = lxml.etree.fromstring('<xml/>')
        for a_id in missing_ids:
            element = lxml.etree.Element('assessmentitem')
            element.set('id', a_id)
            element.text = 'Assessment item %s' % a_id
            tree.append(element)
        xml = lxml.etree.tostring(tree)
        creds = (self.user, self.password)
        try:
            result = requests.post(assessments_url, data={'xml':xml}, auth=creds)
            self.assessments_zip = result.content

            zipio = StringIO(self.assessments_zip)
            zipfile = ZipFile(zipio, 'r')
            return None, zipfile
        except ConnectionError:
            return 'Could not connect to %s.' %assessments_url, None

    def import_assessments(self, zipfile):
        errors = imported = []
        assessments_xml = zipfile.open('assessmentitems.xml').read()
        tree = lxml.etree.fromstring(assessments_xml)
        elements = tree.findall('assessmentitem')
        if elements is None or len(elements) < 1:
            return errors, []
        
        activities = self.portal._getOb('activities')
        for count, element in enumerate(elements):
            print 'Importing assessment item %s of %s' % (count+1, len(elements)) 
            #obj = activities.createObjectInContainer
            imported.append('Imported assessment item %s' % element.get('id'))
            
        return errors, imported
    
    def add_errors(self, errors):
        for error in errors: 
            msg = _(error)
            IStatusMessage(self.request).addStatusMessage(msg, u"error")

    def add_messages(self, messages):
        for message in messages:
            msg = _(message)
            IStatusMessage(self.request).addStatusMessage(msg, u"info")
