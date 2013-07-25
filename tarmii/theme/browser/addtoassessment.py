from five import grok
from zope.interface import Interface
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from plone.i18n.normalizer.interfaces import IURLNormalizer
#from plone.app.content.namechooser import NormalizingNameChooser
from plone.dexterity.utils import createContentInContainer

from z3c.relationfield import RelationValue
from Products.CMFCore.utils import getToolByName

grok.templatedir('templates')

class AddToAssessmentView(grok.View):
    """ View for selecting which assessments (tests) an assessment item
        (activity) must be added to.
    """
    grok.context(Interface) 
    grok.name('add-to-assessment')
    grok.template('addtoassessment')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):

        activity_id = self.request.get('activity_id', '')
        catalog = getToolByName(self.context, 'portal_catalog')
        brain = catalog.searchResults(
                    portal_type='upfront.assessmentitem.content.assessmentitem',
                    id=activity_id)
        assessmentitem = brain[0].getObject()

        if self.request.form.has_key('buttons.add.to.assessment.cancel'):
            # Redirect to the activities listing - which should be the context            
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        # check if form has been submitted
        if self.request.form.has_key('buttons.add.to.assessment.submit'):
            new_assessment =\
                self.request.form['buttons.add.to.assessment.text.input']
            # anything typed into input takes prescedence over dropdown select
            if new_assessment != '':
                brains = catalog.searchResults(
                            portal_type='upfront.assessment.content.assessment')
                assessment_list = []
                for brain in brains:
                    assessment_list.append(brain.id)

                # create new assessment in assessments folder
                pm = getToolByName(self.context, 'portal_membership')
                members_folder = pm.getHomeFolder()

                # see explanation in assessments method why we do next 3 
                # lines instead of "members_folder._getOb('assessments')"
                ls = [x.getObject().Title() for x in 
                                        members_folder.getFolderContents()]
                idx = ls.index('Assessments')
                assessments_folder = members_folder.getFolderContents()\
                                                        [idx].getObject()

                assessment = createContentInContainer(assessments_folder,
                                 'upfront.assessment.content.assessment')
                assessment.title = new_assessment

            else:
                # get selected assessment from dropdown
                selected = self.request.get('assessment_uid_selected', '')
                if selected != '': 
                    brain = catalog.searchResults(
                            portal_type='upfront.assessment.content.assessment',
                            UID=selected)
                    assessment = brain[0].getObject()
                else:
                    # being here means that we have no specified a new
                    # assessment, and this activity already exists in all 
                    # existing assessments, which means that the list of
                    # availble assessments is empty
                    return self.request.RESPONSE.redirect(
                                                    self.context.absolute_url())

            # if we arrived here, we have obtained a valid assessment object,
            # associate the activity with it

            intids = getUtility(IIntIds)
            assessmentitem_intid = intids.getId(assessmentitem)

            assessment_items = assessment.assessment_items
            assessment_items.append(RelationValue(assessmentitem_intid))
            assessment.assessment_items = assessment_items
            notify(ObjectModifiedEvent(assessment))           

            self.request.RESPONSE.redirect(self.context.absolute_url())

    def activity_id(self):
        """ return activity_id so that it can be reposted in a new request """
        return self.request.get('activity_id', '')

    def available_assessments(self):
        """ Return all assessments of the current logged in user that do not
            contain the specified activity yet.
        """

        activity_id = self.request.get('activity_id', '')

        # get users' assessments folder and its contents
        pm = getToolByName(self.context, 'portal_membership')
        members_folder = pm.getHomeFolder()

        # following 3 lines need explaining, we could have instead used:
        # assessments_folder = members_folder._getOb('assessments'), but we
        # needed to get the get the assessments folder object without knowing
        # what its id will be, as unit tests might at times set the id
        # 'assessments_', whereas the real live site will use 'assessments'
        # setting id to 'assessments_' at testing was necessary to enable testof
        # the assessments folder creation in eventhandlers, so if we already had
        # 'assessments' in the system prior, it would flag as duplicate.        
        ls = [x.getObject().Title() for x in members_folder.getFolderContents()]
        idx = ls.index('Assessments')
        assessments_folder = members_folder.getFolderContents()[idx].getObject()

        contentFilter={"portal_type" : 'upfront.assessment.content.assessment'}
        brains = assessments_folder.getFolderContents(contentFilter)

        available_assessments = []
        for brain in brains:
            assessment = brain.getObject()
            # for each assessment object, go through list of assessment_items
            ids_list = [x.to_object.id for x in assessment.assessment_items]
            if not activity_id in ids_list:
                available_assessments.append(brain)

        return available_assessments
