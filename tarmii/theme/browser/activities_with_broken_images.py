import re
import logging

from five import grok
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from plone.app.textfield import RichText

from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from tarmii.theme.behaviors import IItemMetadata
from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme import MessageFactory as _


IMAGE_EXP = re.compile('src=\"(.*?)\"')
RESOLVE_EXP = re.compile('src=\"resolveuid/(.*?)\"')

CONTENT_ATTR_NAMES = {
    'activity': IItemMetadata.get('activity'),
    'content_concept_skills': IItemMetadata.get('content_concept_skills'),
    'prior_knowledge_skills': IItemMetadata.get('prior_knowledge_skills'),
    'equipment_and_administration': IItemMetadata.get('equipment_and_administration'),
}

grok.templatedir('templates')

class ActivitiesWithBrokenImages(grok.View):
    """ Activities with broken image refs.
    """

    grok.context(Interface)
    grok.name('activities-with-broken-images')
    grok.template('activities_with_broken_images')
    grok.require('zope2.View')

    def update(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type': 'upfront.assessmentitem.content.assessmentitem'}
        brains = pc(query)

        self._images = {}
        for count, brain in enumerate(brains):
            print '=================================================================='
            print 'Checking item %s of %s' % (count, len(brains))
            item = brain.getObject()
            for name, field in CONTENT_ATTR_NAMES.items():
                if isinstance(field, RichText):
                    value = IItemMetadata.get(name).get(item)
                    if value is not None:
                        image_refs = self.check_images(value.raw, pc)
                        if image_refs:
                            self._images[item] = image_refs
    
    def images(self):
        return self._images

    def check_images(self, content, pc):
        uids = RESOLVE_EXP.findall(content) 
        print uids
        query = {'UID': uids}
        brains = pc(query)
        print brains
        # if we find uids, but they are not in the catalog.
        if len(uids) > 0 and len(brains) == 0:
            return uids
        return []
