from zope.interface import Interface
from five import grok

grok.templatedir('templates')

class ActivitiesView(grok.View):
    """ View for activities folder
    """
    grok.context(Interface)
    grok.name('activities')
    grok.template('activities')
    grok.require('zope2.View')

    def activities(self):
        """ Return all the activities in the current folder
        """
        contentFilter = {
            'portal_type': 'upfront.assessmentitem.content.assessmentitem'}
        return self.context.getFolderContents(contentFilter)

