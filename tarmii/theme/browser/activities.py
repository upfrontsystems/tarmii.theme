from sets import Set
from five import grok

from AccessControl import getSecurityManager
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import Interface
from zope.container.interfaces import INameChooser

from zc.relation.interfaces import ICatalog
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from plone.i18n.normalizer.interfaces import IURLNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFCore.permissions import ManagePortal

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

        return self.topics

    def user_is_admin(self):
        """ Test if add activity is accessed by an admin user
            has "ManagePortal" Permission on the activities folder
        """
        return getSecurityManager().checkPermission(ManagePortal,self.context)

    def topictrees(self):
        """ Return all topic trees in the system that are tagged to be used 
            with activities view.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_activities:
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

        if self.request.form.has_key('buttons.search.activity.submit'):
            search_id = self.request.form['buttons.search.activity.input']
            normalizer = getUtility(IURLNormalizer)
            item_id = normalizer.normalize(str(search_id))
            results = catalog(id=item_id)
        elif len(self.topics) == 0:
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

    def activities_batch(self):
        """ Return activities that match current filter criteria.
            Return batched.
        """
        b_size = 10
        b_start = self.request.get('b_start', 0)
        return Batch(self.activities(), b_size, int(b_start), orphan=0)

    def activities_count(self):
        """ Return number of activities that match current filter criteria
        """
        return len(self.activities())

    def search_value(self):
        """ Return the id of the activity that the user searched for
        """
        if self.request.form.has_key('buttons.search.activity.submit'):
            return self.request.form['buttons.search.activity.input']
        return ''

