from sets import Set
from five import grok

from AccessControl import getSecurityManager
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getAdapterInContext
from zope.interface import Interface
from zope.container.interfaces import INameChooser

from zc.relation.interfaces import ICatalog
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from plone.i18n.normalizer.interfaces import IURLNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFCore.permissions import ManagePortal

from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from tarmii.theme.interfaces import IActivityCloner
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

    def export_csv_url(self):
        """ return link to export activities view """
        return '%s/@@export-activities' % self.context.absolute_url()

    def export_pdf_url(self):
        """ return link to export activities pdf """
        return '%s/@@activities-pdf' % self.context.absolute_url()

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

    def activities(self):
        """ Return activities that match current filter criteria.
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        show_my_activities = self.request.form.get('show_my_activities')
        pps = self.context.restrictedTraverse('@@plone_portal_state')
        creator = pps.member().getId()
        if self.request.form.has_key('buttons.search.activity.submit'):
            search_id = self.request.form['buttons.search.activity.input']
            normalizer = getUtility(IURLNormalizer)
            item_id = normalizer.normalize(str(search_id))
            results = catalog(id=item_id)
        else:
            query = {
                'portal_type': 'upfront.assessmentitem.content.assessmentitem'
            }
            if show_my_activities:
                query['Creator'] = creator
            if self.topics:
                query['topic_uids'] = {'query': self.topics, 'operator': 'and'}
            results = catalog(query)

        return results

    def review_state_title(self, obj):
        wftool = getToolByName(obj, 'portal_workflow')
        state = wftool.getInfoFor(obj, 'review_state')
        for wf in wftool.getWorkflowsFor(obj):
            if state in wf.states.keys():
                return wf.states[state].title

    def activities_batch(self):
        """ Return activities that match current filter criteria.
            Return batched.
        """
        b_size = 10
        b_start = self.request.get('b_start', 0)
        return Batch(self.activities(), b_size, int(b_start), orphan=0)

    def search_value(self):
        """ Return the id of the activity that the user searched for
        """
        if self.request.form.has_key('buttons.search.activity.submit'):
            return self.request.form['buttons.search.activity.input']
        return ''


class CloneActivity(grok.View):
    """ Clone the current activity.
    """
    grok.context(IAssessmentItem)
    grok.name('clone')
    grok.require('zope2.View')

    def update(self):
        activity = self.context
        container = activity.aq_parent
        adapter = getAdapterInContext(activity, IActivityCloner, container)
        self.clone = adapter.clone(activity)

    def render(self):
        """ Keep grok happy with no-op
        """
        url = self.clone.absolute_url() + '/edit'
        self.request.response.redirect(url)
