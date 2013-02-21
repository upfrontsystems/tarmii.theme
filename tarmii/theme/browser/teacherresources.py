import json
from five import grok

from AccessControl import getSecurityManager

from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import AddPortalContent

from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class TeacherResourcesView(grok.View):
    """ A view to display the all the teacher resources in the system.
    """
    grok.context(Interface)
    grok.name('teacher-resources')
    grok.template('teacher-resources')
    grok.require('zope2.View')

    def topictrees(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        return brains

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


