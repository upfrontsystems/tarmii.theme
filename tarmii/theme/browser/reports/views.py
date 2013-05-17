import datetime
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
from tarmii.theme.browser.reports.charts import ClassProgressChart
from tarmii.theme.browser.reports.charts import LearnerProgressChart

grok.templatedir('templates')

class ReportViewsCommon:
    """ Mixin class that provides user_anonymous method.
    """

    def user_anonymous(self):
        """ Raise Unauthorized if user is anonymous
        """
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized("You do not have permission to view this page.")

class DatePickers:
    """ Mixin class that provides datepicker methods.
    """

    def startDateString(self):
        """ return datestring for start date - date picker
        """
        start_date_day = self.request.get('Start-Date_day')
        start_date_month = self.request.get('Start-Date_month')
        start_date_year = self.request.get('Start-Date_year')

        if start_date_day is not None:
            start_date = datetime.date(int(start_date_year),
                                       int(start_date_month),
                                       int(start_date_day))
        else:
            start_date = datetime.datetime.today() - datetime.timedelta(365)

        return start_date.strftime(u'%Y-%m-%d')

    def endDateString(self):
        """ return datestring for end date - date picker
        """
        end_date_day = self.request.get('End-Date_day')
        end_date_month = self.request.get('End-Date_month')
        end_date_year = self.request.get('End-Date_year')

        if end_date_day is not None:
            end_date = datetime.date(int(end_date_year),
                                     int(end_date_month),
                                     int(end_date_day))
        else:
            end_date = datetime.datetime.today()

        return end_date.strftime(u'%Y-%m-%d')

    def end_date_label(self):
        return self.context.translate(_(u'End Date'))

    def start_date_label(self):
        return self.context.translate(_(u'Start Date'))

    def check_date_integrity(self):
        """ returns False if start_date specified is later than the end_date
        """
        start_date = datetime.datetime.strptime(self.startDateString(),
                                                                    u'%Y-%m-%d')
        end_date = datetime.datetime.strptime(self.endDateString(), u'%Y-%m-%d')
        if start_date > end_date:
            return False
        return True    


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


class ClassPerformanceForActivityView(grok.View, ReportViewsCommon):
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


class ClassProgressChartView(grok.View):
    """ Class progress for a given time period
    """
    grok.context(Interface)
    grok.name('classprogress-chart')
    grok.require('zope2.View')

    def data(self):
        # if we are here, evaluationsheets exist in the specified range

        classlist_uid = self.request.get('classlist', '')
        title = self.context.translate(_(u'Class progress'))
        return { 
            'title' : title,
            'value_data' : [
                            (13, 5, 20, 22, 37, 45, 19, 4),
                            (5, 20, 46, 38, 23, 21, 6, 14)
                           ],
            'category_data' : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                               'Jul', 'Aug']
            }

    def render(self):
        request = self.request
        response = request.response

        drawing = ClassProgressChart(self.data())
        out = StringIO(renderPM.drawToString(drawing, 'PNG'))
        response.setHeader('expires', 0)
        response['content-type']='image/png'
        response['Content-Length'] = out.len
        response.write(out.getvalue())
        out.close()


class ClassProgressView(grok.View, ReportViewsCommon, DatePickers):
    """ Class progress report view
    """
    grok.context(Interface)
    grok.name('class-progress')
    grok.template('classprogress')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """ get classlist parameter from request, if none selected pick first
            classlist in classlists folder.
        """

        self.classlist_uid = self.request.get('classlist_uid_selected', '')

        if self.classlist_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(members_folder.classlists.getFolderContents()) == 0:
                # no classlists
                self.classlist_id = ''
                return []
            else:                
                # no classlist selected so pick first one in list
                classlist = members_folder.classlists.getFolderContents()[0]\
                                                                    .getObject()
                self.classlist_uid = IUUID(classlist)

    def classlists(self):
        """ return all of the classlists of the current user
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist',
            'sort_on': 'sortable_title'}
        return members_folder.classlists.getFolderContents(contentFilter)

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter =\
                   {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets =\
                     members_folder.evaluations.getFolderContents(contentFilter)

        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            evaluationsheet_date = datetime.datetime.strptime(obj.created()
                               .asdatetime().strftime(u'%Y-%m-%d'),u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(self.startDateString(),
                                                                    u'%Y-%m-%d')    
            if self.check_date_integrity():
                if evaluationsheet_date >= start_date:
                    evaluationsheets_in_range.append(obj)

        return evaluationsheets_in_range

    def selected_classlist(self):
        return self.classlist_uid


class LearnerProgressView(grok.View, ReportViewsCommon, DatePickers):
    """ Learner progress report view
    """
    grok.context(Interface)
    grok.name('learner-progress')
    grok.template('learnerprogress')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """
        """
        self.classlist_uid = self.request.get('classlist_uid_selected', '')
        self.learner_uid = self.request.get('learner_uid_selected', '')

        if self.classlist_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(members_folder.classlists.getFolderContents()) == 0:
                # no classlists
                self.classlist_id = ''
                return []
            else:                
                # no classlist selected so pick first one in list
                classlist = members_folder.classlists.getFolderContents()[0]\
                                                                    .getObject()
                self.classlist_uid = IUUID(classlist)
                contentFilter = {
                    'portal_type': 'upfront.classlist.content.learner',
                    'sort_on': 'sortable_title'}
                classlist_contents = classlist.getFolderContents(contentFilter)
                if len(classlist_contents) != 0:
                    self.learner_uid = IUUID(classlist_contents[0].getObject())
        elif self.learner_uid == '':
            # this executes when one is picking a classlist with learners
            # after having picked a classlist with no learners
            classlist = uuidToObject(self.classlist_uid)
            contentFilter = { 
                'portal_type': 'upfront.classlist.content.learner',
                'sort_on': 'sortable_title'}
            classlist_contents = classlist.getFolderContents(contentFilter)
            if len(classlist_contents) != 0:
                # pick the first learner from the classlist
                self.learner_uid = IUUID(classlist_contents[0].getObject())

    def classlists(self):
        """ return all of the classlists of the current user
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist',
            'sort_on': 'sortable_title'}
        return members_folder.classlists.getFolderContents(contentFilter)

    def learners(self):
        """ return all of the learners from a specific classlist
        """
        if self.classlist_uid == '':
            return []
        else:
            contentFilter = {
                'portal_type': 'upfront.classlist.content.learner',
                'sort_on': 'sortable_title'}
            classlist = uuidToObject(self.classlist_uid)
            return classlist.getFolderContents(contentFilter)

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter =\
                   {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets =\
                     members_folder.evaluations.getFolderContents(contentFilter)

        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            evaluationsheet_date = datetime.datetime.strptime(obj.created()
                               .asdatetime().strftime(u'%Y-%m-%d'),u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(self.startDateString(),
                                                                    u'%Y-%m-%d')    
            if self.check_date_integrity():
                if evaluationsheet_date >= start_date:
                    evaluationsheets_in_range.append(obj)

        return evaluationsheets_in_range

    def selected_classlist(self):
        return self.classlist_uid

    def selected_learner(self):
        return self.learner_uid

    def getUID(self, obj):
        return IUUID(obj)


class StrengthsAndWeaknessesView(grok.View, ReportViewsCommon, DatePickers):
    """ Strengths And Weaknesses report view
    """
    grok.context(Interface)
    grok.name('strengths-and-weaknesses')
    grok.template('strengths-and-weaknesses')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """
        """
        return True


class EvaluationSheetView(grok.View, ReportViewsCommon, DatePickers):
    """ Evaluationsheet report view
    """
    grok.context(Interface)
    grok.name('evaluationsheet')
    grok.template('evaluationsheet')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """
        """
        return True



