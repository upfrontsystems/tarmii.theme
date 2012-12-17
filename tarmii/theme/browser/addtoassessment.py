from zope.interface import Interface
from five import grok

from Products.CMFCore.utils import getToolByName

grok.templatedir('templates')

class AddToAssessmentView(grok.View):
    """ View for selecting which assessments (tests) an assessment item
        (activity) must be added to.
    """
    grok.context(Interface) # XXX Perhaps change this to assessmentitem only?
    grok.name('add-to-assessment')
    grok.template('addtoassessment')
    grok.require('zope2.View')

    def assessments(self):
        """ Return all assessments of the current logged in user
        """

        #get users' assessments folder and its contents
        pm = getToolByName(self.context, 'portal_membership')
        members_folder = pm.getHomeFolder()
        assessments_folder = members_folder._getOb('assessments')

        contentFilter={"portal_type" : 'upfront.assessment.content.assessment'}
        brains = assessments_folder.getFolderContents(contentFilter)        

        return brains
