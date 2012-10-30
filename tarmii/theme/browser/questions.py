from zope.interface import Interface
from five import grok
from plone.dexterity.utils import createContentInContainer
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

    def update(self):
        if not self.request.has_key('form.submitted'):
            return
        obj = createContentInContainer(self.context,
            'upfront.assessmentitem.content.assessmentitemcontainer')
        createContentInContainer(obj,
            'upfront.assessmentitem.content.assessmentitem')
        self.request.RESPONSE.redirect(obj.absolute_url() + '/edit')
