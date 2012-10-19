from five import grok
from zope.interface import Interface
from collective.topictree.topictree import ITopicTree

grok.templatedir('templates')

class TopicTreesView(grok.View):
    """ View for topic trees folder
    """
    grok.context(Interface)
    grok.name('topictrees')
    grok.template('topictrees')
    grok.require('cmf.ModifyPortalContent')

    def topictrees(self):
        """ Return all the topic trees in the current folder
        """
        return self.context.getFolderContents()

    def add_topictree_url(self):
        """ URL for topictree add form
        """
        return "%s/++add++collective.topictree.topictree" % (
            self.context.absolute_url())
