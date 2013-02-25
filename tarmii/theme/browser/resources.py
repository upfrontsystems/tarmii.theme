from sets import Set
from five import grok

from AccessControl import getSecurityManager
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFPlone.PloneBatch import Batch

from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class ResourcesView(grok.View):
    """ A view to display the all the teacher resources in the system.
    """
    grok.context(Interface)
    grok.name('resources')
    grok.template('resources')
    grok.require('zope2.View')

    def update(self, **kwargs):
        """ store all filter selections that were made in self.topics
        """
        # get all the select-dropdowns from the request, we dont know how many
        # there might be so  get all request keys that start with 'select'
        keys = filter(lambda item: item[0:6] == 'select', self.request.keys())
        self.topics = []
        for x in range(len(keys)):
            if self.request.get(keys[x]) != '':
                self.topics.append(self.request.get(keys[x]))

    def addresource_visible(self):
        """ test if add resource button can be shown based on whether the user
            has "AddPortalContent" Permission on the resouces folder 
        """
        return getSecurityManager().checkPermission(AddPortalContent,
                                                    self.context)

    def add_resource_button_path(self):
        """ Path string for the Add Resource button 
        """
        return '%s/createObject?type_name=File' % self.context.absolute_url()

    def topictrees(self):
        """ Return all topic trees in the system
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        return brains

    def resources(self):
        """ Return resource items that match current filter criteria.
            Batch the result.
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        rc = getToolByName(self.context, 'reference_catalog')

        if len(self.topics) == 0:
            # no filter selected, show all options
            folder_path = '/'.join(self.context.getPhysicalPath())
            results = catalog(path={'query': folder_path, 'depth': 1})
        elif len(self.topics) == 1:
            # one filter selected, show all options
            brains = rc(targetUID=self.topics, relationship='topics')
            UID_list = [ x.getObject().sourceUID for x in brains ]
            results = catalog(UID=UID_list)
        else:
            # more than one filter selected, show all options
            brains = rc(targetUID=self.topics[0], relationship='topics')
            UID_set = Set([ x.getObject().sourceUID for x in brains ])
            for x in range(len(self.topics)-1):
                brains = rc(targetUID=self.topics[x+1], relationship='topics')
                next_set = Set([ x.getObject().sourceUID for x in brains ])
                UID_set = UID_set.intersection(Set(next_set))
            UID_list = list(UID_set)
            results = catalog(UID=UID_list)

        data = [ x.getObject() for x in results]
        b_size = 10
        b_start = self.request.get('b_start', 0)
        return Batch(data, b_size, int(b_start), orphan=0)

    def resource_count(self):
        """ Return number of resource items that match current filter criteria
        """
        return len(self.resources())

