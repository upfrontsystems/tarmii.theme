import unicodedata
from five import grok

from zope.component.hooks import getSite
from plone.directives import dexterity

from upfront.assessment.content.assessment import IAssessment
from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class View(dexterity.DisplayForm):
    grok.layer(ITARMIIThemeLayer)
    grok.context(IAssessment)
    grok.require('zope2.View')
    grok.template('custom-assessment-view')

    def assessment(self):
        """ Return the currently selected assessment
        """
        return self.context.title

    def add_activities_url(self):
        """ url to activities view """
        return '%s/activities' % getSite().absolute_url()

    def topics(self):
        """ Return all the topics in the activities that this assessment 
            references
        """
        activities = [x.to_object for x in self.context.assessment_items]
        topic_list = []
        for activity in activities:
            if hasattr(activity,'topics'):
                topics = activity.topics
                for topic in topics:
                    if topic.to_object.title not in topic_list:
                        # convert to string from unicode if necessary
                        if isinstance(topic.to_object.title, unicode):    
                            topic_string = unicodedata.normalize('NFKD',
                                topic.to_object.title).encode('ascii','ignore')
                            topic_list.append(topic_string)
                        else:
                            topic_list.append(topic.to_object.title)

        topic_list.sort(key=str.lower)
        return topic_list

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



