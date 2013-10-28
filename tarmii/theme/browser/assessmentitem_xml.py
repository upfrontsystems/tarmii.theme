import re
import lxml
import logging
import requests
from zipfile import ZipFile
from cStringIO import StringIO
from types import UnicodeType

from datetime import datetime
from DateTime import DateTime

from five import grok
from zope.component import getUtility
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from plone.app.textfield import RichText

from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from tarmii.theme.behaviors import IItemMetadata
from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme import MessageFactory as _

LOG = logging.getLogger('Assessmentite_xml:')

IMAGE_EXP = re.compile('src=\"(.*?)\"')

NAMES_AND_DESCRIPTIONS = IAssessmentItem.namesAndDescriptions() + \
                         IItemMetadata.namesAndDescriptions()

class AssessmentItemXML(grok.View):
    """ Return assessment items as XML.
    """

    grok.context(Interface)
    grok.name('assessmentitem-xml')
    grok.require('zope2.View')

    def update(self):
        zipio = StringIO()
        zipfile = ZipFile(zipio, 'w')

        self.portal_encoding = 'utf-8'
        xml = self.request.form.get('xml')
        if xml is None or len(xml) < 1:
            raise RuntimeError('No xml payload provided!')

        assessments_tree = lxml.etree.fromstring('<xml/>')
        assessments_tree.attrib['encoding'] = self.portal_encoding

        ids_tree = lxml.etree.fromstring(xml)
        ids = [e.get('id') for e in ids_tree.findall('assessmentitem')]
        if ids is not None:
            pc = getToolByName(self.context, 'portal_catalog')
            query = {'portal_type': 'upfront.assessmentitem.content.assessmentitem',
                     'getId': ids}
            brains = pc(query)
            for brain in brains:
                item = brain.getObject()
                element = self.marshal_item(item)
                assessments_tree.append(element)
                self.add_images_to_zip(item, zipfile)

        xml_content = lxml.etree.tostring(assessments_tree)
        zipfile.writestr('assessmentitems.xml', xml_content)
        zipfile.close()
        zipio.seek(0)
        self.content = zipio.read()
        zipio.close()

    def marshal_item(self, assessmentitem):
        element = lxml.etree.Element('assessmentitem')
        element.set('id', assessmentitem.getId())
        element.text = assessmentitem.Title()

        for fname, field in NAMES_AND_DESCRIPTIONS:
            sub_element = lxml.etree.Element(fname)
            attribs = {}
            value = getattr(assessmentitem, fname, u'')
            # If we have a value and it is a RichText field.
            if value is not None and isinstance(field, RichText):
                value = getattr(assessmentitem, fname).raw
                attribs['mimeType'] = field.default_mime_type
                attribs['outputMimeType'] = field.output_mime_type
            # If we have a value, but it is not unicode
            if value is not None and not isinstance(value, UnicodeType):
                value = unicode(value, self.portal_encoding)
            sub_element.attrib.update(attribs)
            sub_element.text = value
            element.append(sub_element)
        return element

    def add_images_to_zip(self, assessmentitem, zipfile):
        pc = getToolByName(self.context, 'portal_catalog')
        for fname, field in NAMES_AND_DESCRIPTIONS:
            images = []
            if not hasattr(assessmentitem, fname):
                LOG.warn('Item %s has no attribute %s. This should not happen.'
                    % (assessmentitem.getId(), fname))
                
            value = getattr(assessmentitem, fname, None)
            if value is not None and isinstance(field, RichText):
                value = value.raw
                image_paths= IMAGE_EXP.findall(value)
                for path in image_paths:
                    # embedded, inline image
                    if path.startswith('data:image'):
                        # we could do something like:
                        # f_image = path
                        # image_id = 'image-%s' % str(len(assessmentitem.objectIds())+1)
                        # zipfile.writestr('images/%s' % image_id, f_image)
                        # but for the moment we just leave it in-line.
                        continue
                    else:
                        image = None
                        if 'resolveuid' in path:
                            result = requests.get(path)
                            image = result.content
                        else:
                            image = assessmentitem.restrictedTraverse([path])
                            f_image = image.getImageAsFile()
                            image = f_image.read()
                            f_image.close()
                        zipfile.writestr('images/'+path, image)


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
