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


class AssessmentItemsIdsXML(grok.View):
    """ Return assessment items ids and titles list as XML.
    """

    grok.context(Interface)
    grok.name('assessmentitem-ids-xml')
    grok.require('zope2.View')

    def update(self):
        import pdb;pdb.set_trace()
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
        return self.xml_content
