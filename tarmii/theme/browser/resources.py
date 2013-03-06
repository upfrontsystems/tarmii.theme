from sets import Set
from five import grok

from AccessControl import getSecurityManager
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import Interface
from zc.relation.interfaces import ICatalog
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import ManagePortal
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
        """ Store all filter selections that were made in self.topics
        """
        # get all the select-dropdowns from the request, we dont know how many
        # there might be so  get all request keys that start with 'select'
        keys = filter(lambda item: item[0:6] == 'select', self.request.keys())
        self.topics = []
        for x in range(len(keys)):
            if self.request.get(keys[x]) != '':
                self.topics.append(self.request.get(keys[x]))

        return self.topics

    def addresource_addportalcontent(self):
        """ Test if add resource button can be shown based on whether the user
            has "AddPortalContent" Permission on the resouces folder 
        """
        return getSecurityManager().checkPermission(AddPortalContent,
                                                    self.context)

    def user_is_admin(self):
        """ Test if the current user is an admin user, test this by checking if
            they have "ManagePortal" Permission on the context
        """
        return getSecurityManager().checkPermission(ManagePortal,self.context)

    def add_resource_button_path(self):
        """ Path string for the Add Resource button 
        """
        return "%s/++add++tarmii.theme.content.teacherresource" % (
                self.context.absolute_url())

    def topictrees(self):
        """ Return all topic trees in the system that are tagged to be used 
            with resources view.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_resources:
                topictree_list.append(x)
        return topictree_list

    def relations_lookup(self,topic_uid):
        """ Return a list of object uids that are referrencing the topic_uid
        """
        ref_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = ref_catalog.findRelations(
                            {'to_id': intids.getId(uuidToObject(topic_uid))})
        rel_list = []
        notfinished = True;
        while notfinished:            
            try:
                rel = result.next()
                if rel.from_object.portal_type ==\
                                         'tarmii.theme.content.teacherresource':
                # only track references from teacherresource objects.
                     rel_list.append(IUUID(rel.from_object))
            except StopIteration:
                notfinished = False;

        return rel_list

    def resources(self):
        """ Return resource items that match current filter criteria.
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        if len(self.topics) == 0:
            # no filter selected, show all options
            folder_path = '/'.join(self.context.getPhysicalPath())
            results = catalog(path={'query': folder_path, 'depth': 1})
            data = [ x.getObject() for x in results]
        elif len(self.topics) == 1:
            # one filter selected, show all options
            rel_list = self.relations_lookup(self.topics[0])
            results = catalog(UID=rel_list)
            data = [ x.getObject() for x in results ]
        else:
            # more than one filter selected, show all options
            UID_set = Set(self.relations_lookup(self.topics[0]))
            for x in range(len(self.topics)-1):
                next_set = Set(self.relations_lookup(self.topics[x+1]))
                UID_set = UID_set.intersection(Set(next_set))
            UID_list = list(UID_set)
            results = catalog(UID=UID_list)
            data = [ x.getObject() for x in results]

        return data

    def resources_batch(self):
        """ Return resource items that match current filter criteria.
            Return batched.
        """
        b_size = 10
        b_start = self.request.get('b_start', 0)
        return Batch(self.resources(), b_size, int(b_start), orphan=0)

    def resource_count(self):
        """ Return number of resource items that match current filter criteria
        """
        return len(self.resources())

