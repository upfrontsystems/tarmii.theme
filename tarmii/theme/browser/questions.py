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

    def add_question_url(self):
        """ URL for topictree add form
        """
        return ('%s/++add++upfront.assessmentitem.content.'
                'assessmentitemcontainer' % (self.context.absolute_url()))
