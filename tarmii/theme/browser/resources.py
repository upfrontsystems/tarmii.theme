from five import grok

from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class ResourcesView(grok.View):
    """ XXX
    """
    grok.context(Interface)
    grok.name('resources')
    grok.template('resources')
    grok.require('zope2.View')

    def find_topic_trees(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        return brains

    def add_resource_button_path(self):
        """ Path string for the Add Resource button
        """
        return '%s/createObject?type_name=File' % self.context.absolute_url()

