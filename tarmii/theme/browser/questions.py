from zope.interface import Interface
from five import grok

grok.templatedir('templates')

class QuestionsView(grok.View):
    """ View for questions folder
    """
    grok.context(Interface)
    grok.name('questions')
    grok.template('questions')
    grok.require('cmf.AddPortalContent')

    def questions(self):
        """ Return all the questions in the current folder
        """
        return self.context.getFolderContents()

