import lxml
import logging
from zipfile import ZipFile
from cStringIO import StringIO

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
            raise RuntimeError('No xml payload provided!')

        assessments_tree = lxml.etree.fromstring('<xml/>')

        ids_tree = lxml.etree.fromstring(xml)
        ids = [e.get('id') for e in ids_tree.findall('assessmentitem')]
        if ids is not None:
            pc = getToolByName(self.context, 'portal_catalog')
            query = {'portal_type': 'upfront.assessmentitem.content.assessmentitem',
                     'getId': ids}
            brains = pc(query)
            for brain in brains:
                element = self.marshal_item(brain.getObject())
                assessments_tree.append(element)

        xml_content = lxml.etree.tostring(assessments_tree)

        zipio = StringIO()
        zipfile = ZipFile(zipio, 'w')
        zipfile.writestr('assessmentitems.xml', xml_content)
        zipfile.close()
        zipio.seek(0)
        self.content = zipio.read()
        zipio.close()

    def marshal_item(self, assessmentitem):
        element = lxml.etree.Element('assessmentitem')
        element.set('id', assessmentitem.getId())
        element.text = assessmentitem.Title()
        return element

    def render(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/octet-stream')
        response.setHeader('Content-Length', len(self.content))
        response.setHeader('Last-Modified', DateTime.rfc822(DateTime()))
        response.setHeader('expires', 0)
        response.setHeader("Content-Disposition",
                           "attachment; filename=%assessmentitems.zip")

        #response.write(self.content)
        return self.content
