from five import grok
from zope.interface import Interface
from collective.topictree.topictree import ITopicTree

from plone.directives import dexterity
grok.templatedir('templates')

class ClassListsView(grok.View):
    """ View for classlist folders
    """
    grok.context(Interface)
    grok.name('classlists')
    grok.template('classlists')
    grok.require('cmf.ModifyPortalContent')

    def classlists(self):
        """ Return all the classlists in the current folder
        """
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist'}
        return self.context.getFolderContents(contentFilter)

    def add_classlist_url(self):
        """ URL for classlist add form
        """
        return "%s/++add++upfront.classlist.content.classlist" % (
            self.context.absolute_url())


class ClassListAddForm(dexterity.AddForm):
    grok.name('upfront.classlist.content.classlist')

    # this method needed so we can reference newly created class list object,
    # that we need in the nextURL method
    def createAndAdd(self, data):
        classlist = super(ClassListAddForm, self).createAndAdd(data)
        # Acquisition wrap patient in the current context
        self.classlist = classlist.__of__(self.context)
        return self.classlist

    def nextURL(self):
        return '%s' % self.classlist.absolute_url()











