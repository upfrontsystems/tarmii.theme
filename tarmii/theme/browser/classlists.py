from five import grok
from zope.interface import Interface
from plone.directives import dexterity
grok.templatedir('templates')

class ClassListsView(grok.View):
    """ View for classlist folders
    """
    grok.context(Interface)
    grok.name('classlists')
    grok.template('classlists')
    grok.require('zope2.View')

    def classlists(self):
        """ Return all the classlists in the current folder
        """
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist',
            'sort_on': 'sortable_title'}
        return self.context.getFolderContents(contentFilter)

    def import_learners_url(self):
        """ URL for importing a new classlist via import-learners view
        """
        return "%s/@@import-learners" % self.context.absolute_url()

    def add_classlist_url(self):
        """ URL for classlist add form
        """
        return "%s/++add++upfront.classlist.content.classlist" % (
            self.context.absolute_url())

    def learner_count(self, classlist):
        """ return number of learners in a classlist
        """
        contentFilter = {
            'portal_type': 'upfront.classlist.content.learner',
            'sort_on': 'sortable_title'}
        return len(classlist.getFolderContents(contentFilter))


class ClassListAddForm(dexterity.AddForm):
    grok.name('upfront.classlist.content.classlist')

    # this method needed so we can reference newly created class list object,
    # that we need in the nextURL method
    def createAndAdd(self, data):
        classlist = super(ClassListAddForm, self).createAndAdd(data)
        # Acquisition wrap classlist in the current context
        self.classlist = classlist.__of__(self.context)
        return self.classlist

    def nextURL(self):
        if self.request.form.has_key('form.buttons.cancel'):
            return self.context.absolute_url()
        else:
            return self.classlist.absolute_url()

