from five import grok
from zope.interface import Interface

grok.templatedir('templates')

class EvaluationSheetsView(grok.View):
    """ View for evaluation folder
    """
    grok.context(Interface)
    grok.name('evaluationsheets')
    grok.template('evaluationsheets')
    grok.require('cmf.ModifyPortalContent')

    def evaluationsheets(self):
        """ Return all the evaluationsheets in the current folder
        """
        contentFilter = {
            'portal_type': 'upfront.assessment.content.evaluationsheet'}
        return self.context.getFolderContents(contentFilter)

    def add_evaluationsheet_url(self):
        """ URL for evaluationsheet add form
        """
        return "%s/++add++upfront.assessment.content.evaluationsheet" % (
            self.context.absolute_url())