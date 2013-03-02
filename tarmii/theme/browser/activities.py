from sets import Set
from five import grok

from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import Interface
from zc.relation.interfaces import ICatalog
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName

from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class ActivitiesView(grok.View):
    """ View for activities folder
    """
    grok.context(Interface)
    grok.name('activities')
    grok.template('activities')
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

    def topictrees(self):
        """ Return all topic trees in the system
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        return brains

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
                            'upfront.assessmentitem.content.assessmentitem':
                # only track references from assessmentitem objects.
                     rel_list.append(IUUID(rel.from_object))
            except StopIteration:
                notfinished = False;

        return rel_list

    def activities(self):
        """ Return activities that match current filter criteria.
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        if len(self.topics) == 0:
            # no filter selected, show all options
            contentFilter = {
                'portal_type': 'upfront.assessmentitem.content.assessmentitem'}
            return self.context.getFolderContents(contentFilter)
        elif len(self.topics) == 1:
            # one filter selected, show all options
            rel_list = self.relations_lookup(self.topics[0])
            results = catalog(UID=rel_list)
        else:
            # more than one filter selected, show all options
            UID_set = Set(self.relations_lookup(self.topics[0]))
            for x in range(len(self.topics)-1):
                next_set = Set(self.relations_lookup(self.topics[x+1]))
                UID_set = UID_set.intersection(Set(next_set))
            UID_list = list(UID_set)
            results = catalog(UID=UID_list)

        return results

    def activities_count(self):
        """ Return number of activities that match current filter criteria
        """
        return len(self.activities())
