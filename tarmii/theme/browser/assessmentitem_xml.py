import lxml
import logging

from datetime import datetime
from DateTime import DateTime

from five import grok
from zope.component import getUtility
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme import MessageFactory as _


class AssessmentItemXML(grok.View):
    """ Return assessment items as XML.
    """

    grok.context(Interface)
    grok.name('assessmentitem-xml')
    grok.require('zope2.View')

    def update(self):
        xml = self.request.form.get('xml')
        if xml is None or len(xml) < 1:
            raise 'No xml payload provided!'
        
        ids_tree = lxml.etree.fromstring(xml)
        ids = [e.get('id') for e in ids_tree.findall('assessmentitem')]
        if ids is None or len(ids) < 1:
            raise 'The xml contains no ids!'

        pc = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type': 'upfront.assessmentitem.content.assessmentitem'}
        brains = pc(query)
        tree = lxml.etree.fromstring('<xml/>')
        for brain in brains:
            element = lxml.etree.Element('assessmentitem')
            element.set('id', brain.getId)
            element.text = 'Assessment item %s' % brain.getId
            tree.append(element)
        self.xml_content = lxml.etree.tostring(tree)

    def render(self):
        response = self.request.response
        response.setHeader('Content-type', 'text/xml')
        response.setHeader('expires', 0)
        response['Content-Length'] = len(self.xml_content)
        response.write(self.xml_content)
