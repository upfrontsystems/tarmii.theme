from five import grok
from zope.interface import Interface
from collective.topictree.topictree import ITopicTree

grok.templatedir('templates')

class ClassListsView(grok.View):
    """ View for classlist folders
    """
    grok.context(Interface)
    grok.name('classlists')
    grok.template('classlists')
    grok.require('cmf.ModifyPortalContent')

    def classlists(self):
        """ Return all the topic trees in the current folder
        """        
        return self.context.getFolderContents()

    def add_classlist_url(self):
        """ URL for classlist add form
        """
        return "%s/++add++upfront.classlist.content.classlist" % (
            self.context.absolute_url())


