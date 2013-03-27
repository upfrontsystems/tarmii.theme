from five import grok
from plone.directives import dexterity

from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.component.hooks import getSite
from zc.relation.interfaces import ICatalog
from plone.directives import dexterity
from plone.uuid.interfaces import IUUID

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class View(dexterity.DisplayForm):
    grok.layer(ITARMIIThemeLayer)
    grok.context(IAssessmentItem)
    grok.require('zope2.View')
    grok.template('assessmentitem-view')

    def assessmentitem(self):
        """ Return the currently selected assessmentitem id
        """
        return self.context.id

    def creationdate(self):
        return self.context.created().strftime('%d %B %Y')

    def review_state(self):
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(self.context, 'review_state')

    def used_in_assessments(self):
        """ Check if activity is used in any assessments.
        """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = catalog.findRelations({
            'to_id': intids.getId(self.context),
            'from_attribute': 'assessment_items'
            })
        try:
            rel = result.next()
            activity_unwrapped = rel.from_object
        except StopIteration:
            return False

        return True
