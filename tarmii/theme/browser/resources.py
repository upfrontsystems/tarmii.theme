import json
from five import grok

from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

from plone.uuid.interfaces import IUUID

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog

from collective.topictree.topictree import ITopicTree
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class ResourcesView(grok.View):
    """ XXX
    """
    grok.context(Interface)
    grok.name('resources')
    grok.template('resources')
    grok.require('zope2.View')

    def topictrees(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        return brains

    def add_resource_button_path(self):
        """ Path string for the Add Resource button
        """
        return '%s/createObject?type_name=File' % self.context.absolute_url()


class GetTreeDataView(grok.View):
    """ Return the JSON representation of the entire Topic Tree
    """
    grok.context(Interface)
    grok.name('gettreedata') 
    grok.require('zope2.View')

    def __call__(self):
        # get the root object uid from the request
        request = self.request
        context_node_uid = request.get('context_node_uid', '')

        # get the JSON representation of the topic tree
        # call topicjson on tree root
        return json.dumps(self.topicjson(context_node_uid))

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''

    def itemcount(self, node_uid):
        """ Return number of resource items that are referenced by topic
        """
        rc = getToolByName(self.context, 'reference_catalog')
        brains = rc(targetUID=node_uid, relationship='topics')
        return len(brains)

    def topicjson(self, node_uid):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(UID=node_uid)
        contents = brains[0].getObject().getFolderContents()
        node_name = brains[0].Title

        # node_rel should be default unless it is a root node
        if brains[0].portal_type == 'collective.topictree.topictree':
            node_rel = 'root'
        else:
            node_rel = 'default'
            node_name = node_name + ' (' + str(self.itemcount(node_uid)) + ')'

        data = {
            'data': node_name,
            'attr': {'node_uid': node_uid, 'id': node_uid},
            'rel': node_rel,
            'children': [],
        }

        for brain in contents:
            data['children'].append(self.topicjson(brain.UID))

        return data
