from StringIO import StringIO
from reportlab.graphics import renderPM

from five import grok
from AccessControl import Unauthorized
from zope.app.intid.interfaces import IIntIds
from zope.component.hooks import getSite
from zope.component import getUtility
from zope.interface import Interface
from zc.relation.interfaces import ICatalog

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName

from tarmii.theme import MessageFactory as _

from tarmii.theme.browser.reports.charts import ClassPerformanceForActivityChart

grok.templatedir('templates')

class ClassPerformanceForActivityChartView(grok.View):
    """ Class performance for a given activity
    """
    grok.context(Interface)
    grok.name('classperformance-for-activity-chart')
    grok.require('zope2.View')

    def data(self):
        # if we are here, evaluations exist

        assessment_uid = self.request.get('assessment', '')
        activity_uid = self.request.get('activity', '')

        assessment = uuidToObject(assessment_uid)
        # find all evaluationsheets that reference the chosen assessment
        ref_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = ref_catalog.findRelations(
                 {'to_id': intids.getId(assessment)})
        evalsheet_rel_list = []
        notfinished = True;
        while notfinished:
            try:
                rel = result.next()
                if rel.from_object.portal_type ==\
                      'upfront.assessment.content.evaluationsheet':
                    # only track references from evaluationsheet objects.
                    evalsheet_rel_list.append(rel.from_object)
            except StopIteration:
                notfinished = False;

        # iterate through all evaluations that reference the current assessment
        activity = uuidToObject(activity_uid)

        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()

        rating_scale = {}
        count_dict = {}
        lookup_dict = {}
        for evalsheet in members_folder.evaluations.getFolderContents():
            if evalsheet.getObject() in evalsheet_rel_list:
                for eval_obj in evalsheet.getObject().getFolderContents():
                    # 1 eval_obj/learner
                    for x in range(len(eval_obj.getObject().evaluation)):
                        uid = eval_obj.getObject().evaluation[x]['uid']
                        if activity_uid == uid:
                            # found matching activity data
                            eval_obj.getObject().evaluation[x]
                            # get the rating_scale, init the count and lookup 
                            # dictionaries only once.
                            if rating_scale == {}:
                                rating_scale = eval_obj.getObject()\
                                                  .evaluation[x]['rating_scale']

                                for z in range(len(rating_scale)):
                                    # init the score counter and the lookup dict
                                    count_dict[rating_scale[z]['label']] = 0
                                    lookup_dict[rating_scale[z]['rating']] =\
                                                        rating_scale[z]['label']

                            # use lookup dict to interpret ratings
                            rating=eval_obj.getObject().evaluation[x]['rating']
                            # do not add unrated (0) entries and 
                            # explicitly unrated (-1) entries into the count
                            if rating != 0 and rating != -1:
                               count_dict[lookup_dict[rating]] += 1

        # parse count_dict into a format that the charting code accepts
        value_data = ()
        value_labels = []
        category_labels = []

        # iterate over lookup_dict and extract data from count_dict
        # this is because lookup_dict contains the rating scale in correct order
        for value, key in lookup_dict.iteritems():
            value_labels.append(key) 
            value = count_dict[key] # get count data
            value_data = value_data + (value,)
            category_labels.append(str(value))

        # make sure we are not supplying of value_data of all zeros 
        # this can legally happen if no evaluations are graded yet.
        value_data_is_ok = False
        for x in range(len(value_data)):
            if value_data[x] != 0:
                value_data_is_ok = True

        if not value_data_is_ok:
            # make extra entry of 1 to prevent division by 0
            no_data = [self.context.translate(_(u'No evaluation data exists'))]
            value_labels = no_data
            value_data = (1,)
            category_labels = []

        # structure of data required by charting mechanism
        # value_labels = ['Excellent', 'Good', 'Satisfactory',
        #                 'Needs improvement']
        # 'value_data' : (88, 6, 5, 1)   # does not have to add up to 100
        # 'category_labels' : ['label1','label2','label3','label4']

        title = self.context.translate(_(u'Class performance for activity'))
        return { 
            'title' : title,
            'value_labels'   : value_labels,
            'value_data' : value_data,
            'category_labels' : category_labels
            }

    def render(self):
        request = self.request
        response = request.response

        drawing = ClassPerformanceForActivityChart(self.data())
        out = StringIO(renderPM.drawToString(drawing, 'PNG'))
        response.setHeader('expires', 0)
        response['content-type']='image/png'
        response['Content-Length'] = out.len
        response.write(out.getvalue())
        out.close()


class ClassPerformanceForActivityView(grok.View):
    """ Class performance for a given activity
    """
    grok.context(Interface)
    grok.name('classperformance-for-activity')
    grok.template('classperformance-for-activity')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """ store the uid of the request parameters, if they are '',
            initialise them in an intelligent manner to first choices of the 
            options (if applicable)
        """
        self.assessment_uid = self.request.get('assessment_uid_selected', '')
        self.activity_uid = self.request.get('activity_uid_selected', '')

        if self.assessment_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(members_folder.assessments.getFolderContents()) == 0:
                # assessments contains no activities
                self.assessment_id = ''
                return []
            else:                
                # no assessment selected so pick first one in list
                assessment = members_folder.assessments.getFolderContents()[0]\
                                                                    .getObject()
                self.assessment_uid = IUUID(assessment)
                if len(assessment.assessment_items) != 0:
                    self.activity_uid =\
                                 IUUID(assessment.assessment_items[0].to_object)
        elif self.activity_uid == '':
            # this executes when one is picking an assessment with activities
            # after having picked an assessment with no activities
            assessment = uuidToObject(self.assessment_uid)
            if len(assessment.assessment_items) != 0: 
                # pick the first activity from the assessment's activities
                self.activity_uid =\
                                IUUID(assessment.assessment_items[0].to_object)
        else:
            # check that the activity selected is valid for this assessment
            # this scenario can happen when switching assessments from an 
            # eg. assessment1 that contains activity3 but the assessment2 does
            # not
            assessment = uuidToObject(self.assessment_uid)
            act = uuidToObject(self.activity_uid)
            # if activity selected is not in the newly selected assessment
            if not act in [x.to_object for x in assessment.assessment_items]:                
                if len(assessment.assessment_items) != 0:
                    # pick the first activity from the assessment's activities
                    self.activity_uid =\
                                IUUID(assessment.assessment_items[0].to_object)

    def assessments(self):
        """ return all of the assessments of the current user
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        return members_folder.assessments.getFolderContents()

    def activities(self):
        """ return all of the activities of a specific assessment
        """
        if self.assessment_uid == '':
            return []
        else:
            assessment = uuidToObject(self.assessment_uid)
        return assessment.assessment_items

    def selected_assessment(self):
        return self.assessment_uid

    def selected_activity(self):
        return self.activity_uid

    def getUID(self, obj):
        return IUUID(obj)

    def evaluations(self):
        """ returns all evaluationsheets associated with currently selected 
            assessment, at least one of these evaluationsheet must contain 
            evaluations
        """
        if self.assessment_uid == '':
            return []
        if self.activity_uid == '':
            return []

        assessment = uuidToObject(self.assessment_uid)
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if len(members_folder.evaluations.getFolderContents()) == 0:
            # no evaluations
            return []
        else:
            # find all evaluationsheets that reference the chosen assessment
            ref_catalog = getUtility(ICatalog)
            intids = getUtility(IIntIds)
            result = ref_catalog.findRelations(
                     {'to_id': intids.getId(assessment)})
            rel_list = []
            notfinished = True;
            while notfinished:
                try:
                    rel = result.next()
                    if rel.from_object.portal_type ==\
                          'upfront.assessment.content.evaluationsheet':
                        # only track references from evaluation objects.
                        rel_list.append(IUUID(rel.from_object))
                except StopIteration:
                    notfinished = False;
             
            # make sure that there are at least some evaluation objects in the
            # evaluationsheets, ie. the classlists used for generating 
            # evaluations were not empty.            
            for evaluationsheet in rel_list:
                if len(uuidToObject(evaluationsheet).getFolderContents()) != 0:
                    return rel_list
            return []

    def user_anonymous(self):
        """ Raise Unauthorized if user is anonymous
        """
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized("You do not have permission to view this page.")
