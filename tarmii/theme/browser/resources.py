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
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        return brains

    def resources(self):
        """ Return resource items that match current filter criteria.
            Batch the result.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        results = catalog(path={'query': folder_path, 'depth': 1})
        b_size = 10
        b_start = self.request.get('b_start', 0)
        return Batch(results, b_size, int(b_start), orphan=0)

    def resource_count(self):
        """ Return number of resource items that match current filter criteria
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        folder_path = '/'.join(self.context.getPhysicalPath())
        results = catalog(path={'query': folder_path, 'depth': 1})
        return len(results)

