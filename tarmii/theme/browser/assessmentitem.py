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

    def itemid(self):
        """ Return the currently selected assessmentitem item id
        """
        return self.context.item_id

    def creationdate(self):
        return self.context.created().strftime('%d %B %Y')

    def review_state(self):
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(self.context, 'review_state')

    def review_state_title(self):
        state = self.review_state()
        wftool = getToolByName(self.context, 'portal_workflow')
        for wf in wftool.getWorkflowsFor(self.context):
            if state in wf.states.keys():
                return wf.states[state].title

    def topics(self):
        """ Return the topics in this activity
        """
        topic_list = []
        if hasattr(self.context,'topics'):
           topics = self.context.topics
           for topic in topics:
               topic_list.append(topic.to_object.title)

        return topic_list

