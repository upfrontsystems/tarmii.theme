from five import grok
from zope.interface import Interface
from collective.topictree.topictree import ITopicTree

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


class AddQuestionView(grok.View):
    """ Add Questions View
    """
    grok.context(Interface)
    grok.name('addquestion')
    grok.template('addquestion')
    grok.require('cmf.AddPortalContent')

