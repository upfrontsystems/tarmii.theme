from five import grok
from zope.interface import Interface
from plone.directives import dexterity
grok.templatedir('templates')

class AssessmentsView(grok.View):
    """ View for assessment folders
    """
    grok.context(Interface)
    grok.name('assessments')
    grok.template('assessments')
    grok.require('cmf.ModifyPortalContent')

    def assessments(self):
        """ Return all the classlists in the current folder
        """
        contentFilter = {
            'portal_type': 'upfront.assessment.content.assessment'}
        return self.context.getFolderContents(contentFilter)

    def add_assessment_url(self):
        """ URL for assessment add form
        """
        return "%s/++add++upfront.assessment.content.assessment" % (
            self.context.absolute_url())
