import unicodedata
from five import grok

from zope.component.hooks import getSite
from plone.directives import dexterity
from Products.CMFCore.utils import getToolByName

from upfront.assessment.content.assessment import IAssessment
from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class View(dexterity.DisplayForm):
    grok.layer(ITARMIIThemeLayer)
    grok.context(IAssessment)
    grok.require('zope2.View')
    grok.template('assessment-view')

    def assessment(self):
        """ Return the currently selected assessment
        """
        return self.context.title

    def add_activities_url(self):
        """ url to activities view """
        return '%s/activities' % getSite().absolute_url()

    def topictrees(self):
        """ Return all the topic trees that are used for tagging activities
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_activities:
                topictree_list.append(x.getObject())
        return topictree_list

    def topics(self, topictree):
        """ Return the topics in the activities that this assessment 
            references, only return the ones matching the specified topictree
        """
        activities = [x.to_object for x in self.context.assessment_items]
        topic_list = []

        for activity in activities:
            if hasattr(activity,'topics'):
                topics = activity.topics
                for topic in topics:
                    if topic.to_object.aq_parent.id == topictree.id:
                        if topic.to_object.title not in topic_list:
                            # convert to string from unicode if necessary
                            if isinstance(topic.to_object.title, unicode):    
                                topic_string = unicodedata.normalize('NFKD',
                                 topic.to_object.title).encode('ascii','ignore')
                                topic_list.append(topic_string)
                            else:
                                topic_list.append(topic.to_object.title)

        return ', '.join(map(str,topic_list))

    def activities(self):
        """ Return all the activities that this assessment references
        """
        return [x.to_object for x in self.context.assessment_items]

    def first_activity(self):
        """ Return first activity
        """
        return self.context.assessment_items[0].to_object

    def last_activity(self):
        """ Return last activity
        """        
        last_index = len(self.context.assessment_items)-1
        return self.context.assessment_items[last_index].to_object

    def assessment_editable(self):
        """ Check whether the assessment can be edited ie. it is not in use
            by evaluationsheets.
        """
        pw = getSite().portal_workflow
        state = pw.getStatusOf('assessment_workflow',self.context)['state']
        if state == 'editable':
            return True
        return False



