from __future__ import division
from DateTime import DateTime as DT
from sets import Set
import datetime            
import heapq
import operator
from StringIO import StringIO
from reportlab.graphics import renderPM
from xhtml2pdf import pisa
from pyPdf import PdfFileWriter, PdfFileReader

from five import grok
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from AccessControl import Unauthorized
from zope.app.intid.interfaces import IIntIds
from zope.component.hooks import getSite
from zope.component import getUtility, getMultiAdapter
from zope.interface import Interface
from zc.relation.interfaces import ICatalog

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName

from tarmii.theme import MessageFactory as _
from tarmii.theme.browser.reports.charts import ClassPerformanceForActivityChart
from tarmii.theme.browser.reports.charts import ClassProgressChart
from tarmii.theme.browser.reports.charts import LearnerProgressChart

from upfront.assessment.content.evaluation import UN_RATED, NOT_RATED

grok.templatedir('templates')

class DatePickers:
    """ Mixin class that provides datepicker methods for the charting views.
    """

    def check_date_integrity(self):
        """ returns False if start_date specified is later than the end_date
        """
        start_date = datetime.datetime.strptime(self.startDateString(),
                                                u'%Y-%m-%d')
        end_date = datetime.datetime.strptime(self.endDateString(), u'%Y-%m-%d')
        if start_date > end_date:
            return False
        return True    

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

    def start_date_label(self):
        return self.context.translate(_(u'Start Date'))


class ReportViewsCommon(DatePickers):
    """ Mixin class that provides user_anonymous, classlists,
        is_standard_rating_scale, evaluationsheet_filter and average_scores 
        methods.
        These are not necessarily used by all charting views but when more than
        two classes use exactly the same code/method, it is placed here.
    """

    def average_scores(self, evaluationsheets_in_range):
        """ preforms calculations on the specified evaluationsheets
            returns filtered_all_activity_ids, filtered_all_scores,
                    filtered_all_highest_ratings, filtered_all_rating_scales
                    average_all_scores
                    * filtered means, that unrated and non-rated scores are 
                    filtered out of the result
            used by class performance chart and strength and weakness chart
                   
        """
        all_scores = []
        all_learner_count = []
        all_activity_ids = []
        all_activities = []
        all_highest_ratings = []
        all_rating_scales = []

        for evalsheet in evaluationsheets_in_range:
            # this is safe since the evalsheet only allows evaluation objects.
            evaluation_objects = evalsheet.objectValues()

            scores = []
            activity_ids = []
            activities = []
            highest_rating = []
            rating_scales = []
            learner_count = []
            # one ev object per learner
            for ev in evaluation_objects:
                # x iterates through the activities each learner did
                for x in range(len(ev.evaluation)):
                    if scores == []:
                        # init lists so that we can use indexing
                        scores = [0] * len(ev.evaluation)
                        learner_count = [0] * len(ev.evaluation)
                        activity_ids = [None] * len(ev.evaluation)
                        activities = [None] * len(ev.evaluation)
                        highest_rating = [None] * len(ev.evaluation)
                        rating_scales = [None] * len(ev.evaluation)
                        number_of_learners_in_activity = len(ev.evaluation)
                    activity_ids[x] = uuidToObject(ev.evaluation[x]['uid']).id
                    activities[x] = uuidToObject(ev.evaluation[x]['uid'])
                    # dont add unrated/explicitly not_rated scores into the 
                    #average calculation
                    if ev.evaluation[x]['rating'] not in [UN_RATED,NOT_RATED]:
                        scores[x] += ev.evaluation[x]['rating']
                        learner_count[x] += 1
                    rating_scale = ev.evaluation[x]['rating_scale']
                    rating_scales[x] = [0] * len(rating_scale)
                    for y in range(len(rating_scale)):
                        # store the rating scale for activity x
                        rating_scales[x][y] = rating_scale[y]['rating']
                    # sort the stored rating scale highest to lowest (in case
                    # it isnt already the case)
                    rating_scales[x].sort()
                    rating_scales[x].reverse()
                    # find the highest possible rating in this activities rating
                    # scale, needed for reference line on the chart
                    for y in range(len(rating_scale)):
                        if highest_rating[x] < rating_scale[y]['rating']:
                            # update highest_rating if higher rating found than
                            # previously stored rating
                            highest_rating[x] = rating_scale[y]['rating']

            all_learner_count += learner_count
            all_scores += scores
            all_activity_ids += activity_ids
            all_activities += activities
            all_highest_ratings += highest_rating
            all_rating_scales += rating_scales

        # filter out activities which no learners have completed
        filtered_all_highest_ratings = []
        filtered_all_scores = []
        filtered_all_activity_ids = []
        filtered_all_activities = []
        filtered_all_rating_scales = []
        filtered_all_learner_count = []
        for x in range(len(all_scores)):
            if all_learner_count[x] > 0:
                filtered_all_highest_ratings.append(all_highest_ratings[x])
                filtered_all_scores.append(all_scores[x])
                filtered_all_activity_ids.append(all_activity_ids[x])
                filtered_all_activities.append(all_activities[x])
                filtered_all_rating_scales.append(all_rating_scales[x])
                filtered_all_learner_count.append(all_learner_count[x])

        # divide the score of each activity / number of learners that completed
        # the activity
        average_all_scores = [0] * len(filtered_all_scores)
        for x in range(len(filtered_all_scores)):
            average_all_scores[x] = \
                float(filtered_all_scores[x]) / filtered_all_learner_count[x]

        result = [filtered_all_activity_ids, filtered_all_scores,
                  filtered_all_highest_ratings, filtered_all_rating_scales,
                  average_all_scores]

        # filter out activities based on subject and language if the filters are
        # in use 
        if self.topic_filtering_on:
            tf_highest_ratings = [] # tf = topic filtered
            tf_scores = []
            tf_activity_ids = []
            tf_rating_scales = []
            tf_learner_count = []
            for x in range(len(filtered_all_activities)):
                activity = filtered_all_activities[x]
                if hasattr(activity,'topics'):      
                    # get all uids of activity's topics                    
                    uids = [IUUID(k.to_object) for k in activity.topics]
                    if self.subject_uid != '' and self.language_uid != '':
                        if self.subject_uid in uids and \
                           self.language_uid in uids:
                            tf_highest_ratings.append(
                                filtered_all_highest_ratings[x])
                            tf_scores.append(filtered_all_scores[x])
                            tf_activity_ids.append(filtered_all_activity_ids[x])
                            tf_rating_scales.append(
                                filtered_all_rating_scales[x])
                            tf_learner_count.append(
                                filtered_all_learner_count[x])
                    elif self.subject_uid != '':
                        if self.subject_uid in uids:
                            tf_highest_ratings.append(
                                filtered_all_highest_ratings[x])
                            tf_scores.append(filtered_all_scores[x])
                            tf_activity_ids.append(filtered_all_activity_ids[x])
                            tf_rating_scales.append(
                                filtered_all_rating_scales[x])
                            tf_learner_count.append(
                                filtered_all_learner_count[x])
                    elif self.language_uid != '':
                        if self.language_uid in uids:
                            tf_highest_ratings.append(
                                filtered_all_highest_ratings[x])
                            tf_scores.append(filtered_all_scores[x])
                            tf_activity_ids.append(filtered_all_activity_ids[x])
                            tf_rating_scales.append(
                                filtered_all_rating_scales[x])
                            tf_learner_count.append(
                                filtered_all_learner_count[x])

            tf_average_all_scores = [0] * len(tf_scores)
            for x in range(len(tf_scores)):
                tf_average_all_scores[x] = \
                    float(tf_scores[x]) / tf_learner_count[x]

            result = [tf_activity_ids, tf_scores, tf_highest_ratings, 
                      tf_rating_scales, tf_average_all_scores]

        return result

    def classlists(self):
        """ return all of the classlists of the current user
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = { 'portal_type': 'upfront.classlist.content.classlist',
                          'sort_on': 'sortable_title'}
        return members_folder.classlists.getFolderContents(contentFilter)

    def evaluationsheets_filter(self, startdate, enddate, classlist_uid):
        """ return all user's evaluationsheets for the selected date range 
            and only for the selected classlist if classlist_uid is supplied 
            (not None)
        """
        site = getSite()
        pc = getToolByName(self.context, 'portal_catalog')
        pm = getToolByName(self.context, 'portal_membership')
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        startdate = DT(startdate)
        enddate = DT(enddate)
        query = {'portal_type': 'upfront.assessment.content.evaluationsheet',
                 'path': '/'.join(members_folder.getPhysicalPath()),
                 'created': {'query': [startdate, enddate], 'range': 'minmax'}}
        if classlist_uid is not None:
            query['classlist_uid'] = classlist_uid
        brains = pc.unrestrictedSearchResults(query)
        evaluationsheets = [
            site.unrestrictedTraverse(b.getPath()) for b in brains
        ]
        return evaluationsheets

    def evaluationsheets_of_classlist(self):
        """ returns all of the evaluationsheets of the current
            selected classlist
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []

        contentFilter = \
            {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets = \
            members_folder.evaluations.getFolderContents(contentFilter,
                                                         full_objects=True)

        # make sure that we use evaluationsheets only for the selected classlist
        filtered_evalsheet_list = []
        for evalsheet in evaluationsheets:
            classlist = uuidToObject(self.classlist_uid)
            if evalsheet.classlist.to_object == classlist:
                filtered_evalsheet_list.append(evalsheet)

        # sort by created date and show latest evaluationsheets first        
        filtered_evalsheet_list.sort(key=lambda x: x.created())
        filtered_evalsheet_list.reverse()  

        return filtered_evalsheet_list

    def is_standard_rating_scale(self, scale):
        """ test if a rating scale contains 4 ratings and they are numbered 1..4
            (but this will also pass if the ratings are not sorted eg.1,4,3,2)
        """
        if len(scale) != 4:
            return False
        scale_list = []
        for z in range(len(scale)):
            scale_list.append(scale[z]['rating'])
        scale_list.sort()
        for z in range(len(scale_list)):
            if scale_list[z] != z+1:
                return False
        return True

    def is_zero_one_rating_scale(self, scale):
        """ test if a rating scale contains 2 ratings and they are numbered 0 
            and 1 (this will work for 1,0 and 0,1)
        """
        if len(scale) != 2:
            return False
        scale_list = []
        for z in range(len(scale)):
            scale_list.append(scale[z]['rating'])
        scale_list.sort()
        for z in range(len(scale_list)):
            if scale_list[z] != z:
                return False
        return True

    def getCustomTitle(self, evaluationsheet):
        """ returns title for evaluationsheet eg. 'Assessment3 on 31 May 2013'
            and translate the month part of the date
        """
        date = evaluationsheet.created()
        assessment_title = evaluationsheet.assessment.to_object.title        
        on_string = self.context.translate(_(u'on'))
        month = self.context.translate(_(date.strftime('%B')))
        date_string = '%s %s %s' % (date.day(), month, date.year())
        return assessment_title + ' ' + on_string + ' ' + date_string

    def getUID(self, obj):
        return IUUID(obj)

    def languages(self):
        """ return language topics 
        """
        topicfolder = getSite()._getOb('topictrees')
        if topicfolder.hasObject('language'):
            language_folder = topicfolder._getOb('language')
            if len(language_folder.getFolderContents()) != 0:
                return language_folder.getFolderContents()
        return []

    def selected_classlist(self):
        return self.classlist_uid

    def selected_language(self):
        return self.language_uid

    def selected_subject(self):
        return self.subject_uid

    def site_url(self):
        return getToolByName(self.context, 'portal_url')

    def subjects(self):
        """ return subject topics
        """
        topicfolder = getSite()._getOb('topictrees')
        if topicfolder.hasObject('subject'):
            subject_folder = topicfolder._getOb('subject')        
            if len(subject_folder.getFolderContents()) != 0:
                return subject_folder.getFolderContents()
        return []

    def valid_activities(self, evaluation):
        """ returns indexes of activities (in the evaluation)
            that have matched the filters specified
            (expects that self.subject_uid and self.language_uid exist)
        """
        valid_activities = []
        for x in range(len(evaluation)):
            activity = uuidToObject(evaluation[x]['uid'])
            if hasattr(activity,'topics'):      
                # get all uids of activity's topics                    
                uids = [IUUID(k.to_object) for k in activity.topics]

                # now there are 3 scenarios: 
                # lang filter, subject filter both used
                # subject filter used only
                # lang filter used only
                if self.subject_uid != '' and self.language_uid != '':
                    if self.subject_uid in uids and self.language_uid in uids:
                        valid_activities.append(x)
                elif self.subject_uid != '':
                    if self.subject_uid in uids:
                        valid_activities.append(x)
                elif self.language_uid != '':
                    if self.language_uid in uids:
                        valid_activities.append(x)

        return valid_activities
    
    def memberid(self):
        pps = self.context.unrestrictedTraverse('@@plone_portal_state')
        return pps.member().getId()
        
    def user_anonymous(self):
        """ Raise Unauthorized if user is anonymous
        """
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized("You do not have permission to view this page.")


class ClassPerformanceForActivityChartView(grok.View):
    """ Class performance for a given activity
    """
    grok.context(Interface)
    grok.name('classperformance-for-activity-chart')
    grok.require('zope2.View')

    def data(self):
        pc = getToolByName(self.context, 'portal_catalog')
        # if we are here - evaluations and activities exist

        evaluationsheet_uid = self.request.get('evaluationsheet', '')
        activity_uid = self.request.get('activity', '')

        # iterate through all evaluations that reference the current assessment
        #activity = uuidToObject(activity_uid)

        rating_scale = {}
        count_dict = {}
        lookup_dict = {}

        evaluationsheet = pc.unrestrictedSearchResults(
            UID=evaluationsheet_uid)[0]
        query = {'portal_type': 'upfront.assessment.content.evaluation',
                 'path': evaluationsheet.getPath()}
        evaluation_objects = [x.getObject() for x in pc(query)]

        for ev in evaluation_objects:
            # 1 eval_obj/learner
            for x in range(len(ev.evaluation)):
                uid = ev.evaluation[x]['uid']
                if activity_uid == uid:
                    # found matching activity data
                    # get the rating_scale, init the count and lookup 
                    # dictionaries only once.
                    if rating_scale == {}:
                        rating_scale = ev.evaluation[x]['rating_scale']
                        for z in range(len(rating_scale)):
                            # init the score counter and the lookup dict
                            count_dict[rating_scale[z]['label']] = 0
                            lookup_dict[rating_scale[z]['rating']] = \
                                rating_scale[z]['label']

                    # use lookup dict to interpret ratings
                    rating = ev.evaluation[x]['rating']
                    # do not add unrated entries and 
                    # explicitly unrated/not_rated entries into the count
                    if rating != UN_RATED and rating != NOT_RATED:
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
            # append 'learner' or 'learners' to the number of learners.
            if value > 1:
                learner_str = self.context.translate(_(u' learners'))
            else:
                learner_str = self.context.translate(_(u' learner'))
            category_labels.append(str(value) + learner_str)

        # make sure we are not supplying of value_data of all zeros
        # this can legally happen if no evaluations are graded yet.
        # a zero represents that for a specific rating/score, no learners 
        # achieved this. if no learners achieved no scores, we have no data to 
        # show
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
        description = \
            self.context.translate(_(u'Number of learners per rating'))

        # reverse so that the labels show up with 'excellent' first
        # (this will only work for custom scales if people who make custom 
        # scales do not mess with the order and keep it the same as default)
        value_data = value_data[::-1]        
        value_labels.reverse()
        category_labels.reverse()

        return { 
            'title' : title,
            'description' : description,
            'value_labels'   : value_labels,
            'value_data' : value_data,
            'category_labels' : category_labels
            }

    def get_image_data(self):
        drawing = ClassPerformanceForActivityChart(self.data())
        out = StringIO(renderPM.drawToString(drawing, 'PNG'))
        image_data = out.getvalue()
        out.close()
        return image_data

    def render(self):
        request = self.request
        response = request.response

        image_data = self.get_image_data()

        response.setHeader('expires', 0)
        response['content-type']='image/png'
        response['Content-Length'] = len(image_data)
        response.write(image_data)

        return image_data


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
        self.classlist_uid = self.request.get('classlist_uid_selected', '')
        self.evaluationsheet_uid = \
            self.request.get('evaluationsheet_uid_selected', '')
        self.activity_uid = self.request.get('activity_uid_selected', '')

        if self.classlist_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(self.classlists()) == 0:
                # no classlists
                self.classlist_id = ''
                return []
            else:                
                # no classlist selected so pick first one in list
                classlist = self.classlists()[0].getObject()
                self.classlist_uid = IUUID(classlist)

        evaluationsheets = self.evaluationsheets_of_classlist()
        if self.evaluationsheet_uid == '':
            # this executes when one is picking a classlist with 
            # evaluatonsheets after having picked a classlist with no 
            # evaluationsheets
            if len(self.evaluationsheets_of_classlist()) == 0:
                # classlist contains no evaluationsheets
                self.evaluationsheet_uid = ''
                return []
            else:                
                # no evaluationsheet selected so pick first one in list
                ev = evaluationsheets[0]
                assessment = ev.assessment.to_object
                if len(assessment.assessment_items) != 0:
                    self.activity_uid = \
                        IUUID(assessment.assessment_items[0].to_object)
                self.evaluationsheet_uid = IUUID(ev)
        else:
            # check that the evaluationsheet selected is valid for this class
            # this check is necessary when changing classlists            
            ev = uuidToObject(self.evaluationsheet_uid)
            # check if this chosen evaluationsheet is in the selected classlist 
            if not ev in evaluationsheets:
                if len(evaluationsheets) != 0:
                    ev = evaluationsheets[0]
                    assessment = ev.assessment.to_object
                    if len(assessment.assessment_items) != 0:
                        self.activity_uid = \
                            IUUID(assessment.assessment_items[0].to_object)
                    self.evaluationsheet_uid = IUUID(ev)

        if self.activity_uid == '':
            # this executes when one is picking an assessment with activities
            # after having picked an assessment with no activities
            ev = uuidToObject(self.evaluationsheet_uid)
            assessment = ev.assessment.to_object
            if len(assessment.assessment_items) != 0: 
                # pick the first activity from the assessment's activities
                self.activity_uid = \
                    IUUID(assessment.assessment_items[0].to_object)
        else:
            # check that the activity selected is valid for this assessment
            # this scenario can happen when switching assessments from an 
            # eg. assessment1 that contains activity3 but the assessment2 does
            # not
            ev = uuidToObject(self.evaluationsheet_uid)
            assessment = ev.assessment.to_object
            act = uuidToObject(self.activity_uid)
            # if activity selected is not in the newly selected assessment
            if not act in [x.to_object for x in assessment.assessment_items]:                
                if len(assessment.assessment_items) != 0:
                    # pick the first activity from the assessment's activities
                    self.activity_uid = \
                        IUUID(assessment.assessment_items[0].to_object)

    def activities(self):
        """ return all of the activities of a specific assessment
        """
        if self.evaluationsheet_uid == '':
            return []
        else:
            if self.evaluationsheets_of_classlist() == []:
                return []
            ev = uuidToObject(self.evaluationsheet_uid)
            assessment = ev.assessment.to_object
        return assessment.assessment_items

    def evaluations(self):
        """ returns all evaluationsheets associated with currently selected 
            assessment, at least one of these evaluationsheet must contain 
            evaluations
        """
        if self.evaluationsheet_uid == '':
            return []
        if self.activity_uid == '':
            return []
            
        # make sure that there are at least some evaluation objects in the
        # selected evaluationsheet, ie. that the classlists that were used to
        # generate evaluation objects, were not empty.
        if len(uuidToObject(self.evaluationsheet_uid).getFolderContents()) != 0:
            return uuidToObject(self.evaluationsheet_uid).getFolderContents()
        return []

    def selected_evaluationsheet(self):
        return self.evaluationsheet_uid

    def selected_activity(self):
        return self.activity_uid    

    def pdf_url(self):
        return '%s/%s?selected_evaluationsheet=%s&selected_activity=%s' % (
            self.context.absolute_url(),
            '@@classperformance-for-activity-pdf',
            self.selected_evaluationsheet(),
            self.selected_activity()
        )


class ClassProgressChartView(grok.View, ReportViewsCommon):
    """ Class progress for a given time period
    """
    grok.context(Interface)
    grok.name('classprogress-chart')
    grok.require('zope2.View')

    def data(self):
        # if we are here, evaluationsheets exist in the specified date range

        classlist_uid = self.request.get('classlist')
        startdate = self.request.get('startdate', '')
        enddate = self.request.get('enddate', '')
        self.subject_uid = self.request.get('subject', '')
        self.language_uid = self.request.get('language', '') 

        self.topic_filtering_on = False
        if self.subject_uid != '' or self.language_uid != '':
            self.topic_filtering_on = True

        esheets_in_range = \
            self.evaluationsheets_filter(startdate, enddate, classlist_uid)
        
        [filtered_all_activity_ids, filtered_all_scores,
         filtered_all_highest_ratings, filtered_all_rating_scales, 
         average_all_scores] = self.average_scores(esheets_in_range)
         
        title = self.context.translate(_(u'Class Progress'))
        max_score_legend = self.context.translate(_(u'Highest Possible Score'))
        score_legend = self.context.translate(_(u'Average Learner Score'))
        xlabel = self.context.translate(_(u'Activities across time'))
        ylabel = self.context.translate(_(u'Performance Rating'))

        return { 
            'title' : title,
            'value_data' : [
                            tuple(filtered_all_highest_ratings),
                            tuple(average_all_scores)                           
                           ],
            'category_data' : filtered_all_activity_ids,
            'highest_score' : max(filtered_all_highest_ratings),
            'max_score_legend' : max_score_legend,
            'score_legend' : score_legend,
            'xlabel' : xlabel,
            'ylabel' : ylabel
            }
    
    def get_image_data(self):
        drawing = ClassProgressChart(self.data())
        out = StringIO(renderPM.drawToString(drawing, 'PNG'))
        image_data = out.getvalue()
        out.close()
        return image_data

    def render(self):
        request = self.request
        response = request.response

        image_data = self.get_image_data()

        response.setHeader('expires', 0)
        response['content-type']='image/png'
        response['Content-Length'] = len(image_data)
        response.write(image_data)
        return image_data


class ClassProgressView(grok.View, ReportViewsCommon):
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
        self.subject_uid = self.request.get('subject_topic_selected', '')
        self.language_uid = self.request.get('language_topic_selected', '')

        if self.classlist_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(self.classlists()) == 0:
                # no classlists
                self.classlist_id = ''
                return []
            else:                
                # no classlist selected so pick first one in list
                classlist = self.classlists()[0].getObject()
                self.classlist_uid = IUUID(classlist)

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
            and only for the selected classlist
        """
        evaluationsheets_in_range = \
            self.evaluationsheets_filter(self.startDateString(),
                                         self.endDateString(), 
                                         self.classlist_uid)
        return evaluationsheets_in_range

    def evaluation_objects_scored(self): 
        """ make sure that there are at least some evaluation objects that have 
            been scored in any one of the evaluationsheets in range.        
            explicitly not rated scores are regarded as not scored (as they are 
            then later not included in this line chart)
        """
        evaluationsheets_in_range = self.evaluationsheets()
        topic_filtering_on = False
        if self.subject_uid != '' or self.language_uid != '':
            topic_filtering_on = True

        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            for ev in evaluation_objects:
                if topic_filtering_on:
                    activity_indexes = self.valid_activities(ev.evaluation)
                else:
                    activity_indexes = range(len(ev.evaluation))
                for x in activity_indexes:
                    if ev.evaluation[x]['rating'] >= 0:
                        # a score has been found
                        return True
        return False

    def pdf_url(self):
        return '%s/%s?classlist=%s&startdate=%s&enddate=%s&subject=%s&language=%s&memberid=%s' % (
            self.context.absolute_url(),
            '@@classprogress-pdf',
            self.selected_classlist(),
            self.startDateString(),
            self.endDateString(),
            self.selected_subject(),
            self.selected_language(),
            self.memberid())

class LearnerProgressChartView(grok.View, ReportViewsCommon):
    """ Learner progress for a given time period
    """
    grok.context(Interface)
    grok.name('learnerprogress-chart')
    grok.require('zope2.View')

    def data(self):
        # if we are here, evaluationsheets exist in the specified date range

        classlist_uid = self.request.get('classlist', '')
        learner_uid = self.request.get('learner', '')
        startdate = self.request.get('startdate', '')
        enddate = self.request.get('enddate', '')
        self.subject_uid = self.request.get('subject', '')
        self.language_uid = self.request.get('language', '')

        topic_filtering_on = False
        if self.subject_uid != '' or self.language_uid != '':
            topic_filtering_on = True

        evaluationsheets_in_range = \
            self.evaluationsheets_filter(startdate, enddate, classlist_uid)

        all_scores = []
        all_activity_ids = []
        all_activities = []
        all_highest_ratings = []
        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            scores = []
            activity_ids = []
            activities = []
            highest_rating = []
            for ev in evaluation_objects:
                # only use the score data of the specified learner
                valid_activities = []
                if ev.learner.to_object == uuidToObject(learner_uid):
                    if scores == []:
                        # init lists so that we can use indexing
                        # one bucket/activity
                        scores = [UN_RATED] * len(ev.evaluation)
                        activity_ids = [None] * len(ev.evaluation)
                        activities = [None] * len(ev.evaluation)
                        highest_rating = [None] * len(ev.evaluation)
                    for x in range(len(ev.evaluation)):
                        activity_ids[x] = \
                            uuidToObject(ev.evaluation[x]['uid']).id
                        activities[x] = uuidToObject(ev.evaluation[x]['uid'])
                        scores[x] = ev.evaluation[x]['rating']
                        # find the highest possible rating in this activities 
                        # rating scale
                        rating_scale = ev.evaluation[x]['rating_scale']
                        for y in range(len(rating_scale)):
                            if highest_rating[x] < rating_scale[y]['rating']:
                                # update highest_rating if higher rating found
                                # than previously stored rating
                                highest_rating[x] = rating_scale[y]['rating']

            all_scores += scores
            all_activity_ids += activity_ids
            all_activities += activities
            all_highest_ratings += highest_rating

        learner_string = ': ' + uuidToObject(learner_uid).Title()
        title = self.context.translate(_(u'Learner Progress')) + learner_string
        max_score_legend = self.context.translate(_(u'Highest Possible Score'))
        score_legend = self.context.translate(_(u'Learner Score'))
        xlabel = self.context.translate(_(u'Activities across time'))
        ylabel = self.context.translate(_(u'Performance Rating'))

        # filter out activities which this learner has not completed
        # (unrated or "Not rated")
        filtered_all_highest_ratings = []
        filtered_all_scores = []
        filtered_all_activities = []
        filtered_all_activity_ids = []
        for x in range(len(all_scores)):
            if all_scores[x] >= 0:
                filtered_all_highest_ratings.append(all_highest_ratings[x])
                filtered_all_scores.append(all_scores[x])
                filtered_all_activity_ids.append(all_activity_ids[x])
                filtered_all_activities.append(all_activities[x])

        chart_data = { 'title' : title,
                       'value_data' : [
                                       tuple(filtered_all_highest_ratings),
                                       tuple(filtered_all_scores)
                                      ],
                       'category_data' : filtered_all_activity_ids,
                       'highest_score' : max(filtered_all_highest_ratings),
                       'max_score_legend' : max_score_legend,
                       'score_legend' : score_legend,
                       'xlabel' : xlabel,
                       'ylabel' : ylabel
                       }

        # filter out activities based on subject and language if the filters are
        # in use 
        if topic_filtering_on:
            tf_highest_ratings = [] # tf = topic filtered
            tf_scores = []
            tf_activity_ids = []
            for x in range(len(filtered_all_activities)):
                activity = filtered_all_activities[x]
                if hasattr(activity,'topics'):      
                    # get all uids of activity's topics                    
                    uids = [IUUID(k.to_object) for k in activity.topics]
                    if self.subject_uid != '' and self.language_uid != '':
                        if self.subject_uid in uids and \
                           self.language_uid in uids:
                            tf_highest_ratings.append(
                                filtered_all_highest_ratings[x])
                            tf_scores.append(filtered_all_scores[x])
                            tf_activity_ids.append(filtered_all_activity_ids[x])
                    elif self.subject_uid != '':
                        if self.subject_uid in uids:
                            tf_highest_ratings.append(
                                filtered_all_highest_ratings[x])
                            tf_scores.append(filtered_all_scores[x])
                            tf_activity_ids.append(filtered_all_activity_ids[x])
                    elif self.language_uid != '':
                        if self.language_uid in uids:
                            tf_highest_ratings.append(
                                filtered_all_highest_ratings[x])
                            tf_scores.append(filtered_all_scores[x])
                            tf_activity_ids.append(filtered_all_activity_ids[x])

            chart_data = { 'title' : title,
                           'value_data' : [
                                           tuple(tf_highest_ratings),
                                           tuple(tf_scores)
                                          ],
                           'category_data' : tf_activity_ids,
                           'highest_score' : max(tf_highest_ratings),
                           'max_score_legend' : max_score_legend,
                           'score_legend' : score_legend,
                           'xlabel' : xlabel,
                           'ylabel' : ylabel
                           }

        return chart_data

    def get_image_data(self):
        drawing = LearnerProgressChart(self.data())
        out = StringIO(renderPM.drawToString(drawing, 'PNG'))
        image_data = out.getvalue()
        out.close()
        return image_data

    def render(self):
        request = self.request
        response = request.response

        image_data = self.get_image_data()

        response.setHeader('expires', 0)
        response['content-type']='image/png'
        response['Content-Length'] = len(image_data)
        response.write(image_data)
        return image_data


class LearnerProgressView(grok.View, ReportViewsCommon):
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
        self.subject_uid = self.request.get('subject_topic_selected', '')
        self.language_uid = self.request.get('language_topic_selected', '')
        self.startdate = self.request.get('startdate', self.startDateString())
        self.enddate = self.request.get('enddate', self.endDateString())


        if self.classlist_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(self.classlists()) == 0:
                # no classlists
                self.classlist_id = ''
                return []
            else:                
                # no classlist selected so pick first one in list
                classlist = self.classlists()[0].getObject()
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
        else:
            # check that the learner selected is valid for this classlist
            # if not, pick first learner from the now selected classlist
            # (if it is not empty)
            # this scenario will happen when switching between classlists
            # as learners are unique to a classlist
            classlist = uuidToObject(self.classlist_uid)
            learner = uuidToObject(self.learner_uid)

            contentFilter = {'portal_type': 'upfront.classlist.content.learner',
                             'sort_on': 'sortable_title'}
            classlist_contents = classlist.getFolderContents(contentFilter,
                                                             full_objects=True)
            # if activity selected is not in the newly selected assessment
            if not learner in [x for x in classlist_contents]:
                if len(classlist_contents) != 0:
                    # pick the first learner from the classlist's learners
                    self.learner_uid = IUUID(classlist_contents[0])
                else: 
                    self.learner_uid = ''

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
            and only for the selected classlist
        """
        evaluationsheets_in_range = \
            self.evaluationsheets_filter(self.startDateString(), 
                                         self.endDateString(), 
                                         self.classlist_uid)
        return evaluationsheets_in_range

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

    def learner_has_score(self): 
        """ make sure that the selected learner has at least one scored 
            evaluation object in the selected evaluationsheets
            explicitly not rated scores are regarded as not scored (as they are 
            then later not included in this line chart)
        """
        evaluationsheets_in_range = self.evaluationsheets()
        topic_filtering_on = False
        if self.subject_uid != '' or self.language_uid != '':
            topic_filtering_on = True

        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            for ev in evaluation_objects:
                if ev.learner.to_object == uuidToObject(self.learner_uid):
                    if topic_filtering_on:
                        activity_indexes = self.valid_activities(ev.evaluation)
                    else:
                        activity_indexes = range(len(ev.evaluation))
                    for x in activity_indexes:
                        if ev.evaluation[x]['rating'] >= 0:
                            # a score has been found
                            return True

        return False

    def selected_learner(self):
        return self.learner_uid

    def pdf_url(self):
        return '%s/%s?classlist=%s&learner=%s&startdate=%s&enddate=%s&subject=%s&language=%s' % (
            self.context.absolute_url(),
            '@@learnerprogress-pdf',
            self.classlist_uid,
            self.learner_uid,
            self.startdate,
            self.enddate,
            self.subject_uid,
            self.language_uid)


class StrengthsAndWeaknessesBase(ReportViewsCommon):
    """
    """
    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """ calculate the two activities in which the users performed the best
            on average and the two activities in which the users performed the 
            worst on average
        """
        self.not_enough_data = False
        esheets_in_range = self.evaluationsheets()
        if esheets_in_range == []:
            return

        self.topic_filtering_on = False # self.average_scores needs to know this
        [filtered_all_activity_ids, filtered_all_scores,
         filtered_all_highest_ratings, filtered_all_rating_scales, 
         average_all_scores] = self.average_scores(esheets_in_range)

        # combine average_all_scores with filtered_all_activity_ids
        id_scores = []
        for x in range(len(average_all_scores)):
            percent = average_all_scores[x] / filtered_all_highest_ratings[x]
            id_scores.append((filtered_all_activity_ids[x], percent))

        highest = heapq.nlargest(2, id_scores, key=operator.itemgetter(1))
        lowest = heapq.nsmallest(2, id_scores, key=operator.itemgetter(1))
    
        # make sure we have enough data to calculate the report
        if len(highest) < 2 or len(lowest) < 2:
            self.highest_lowest_activities = ['x', 'x', 'x', 'x']
            self.not_enough_data = True
            return

        self.highest_lowest_activities = [highest[0][0], highest[1][0],
                                          lowest[0][0], lowest[1][0]]

    def activity(self, index):
        """ returns an activity from the highest_lowest activities list
            activity is specified via index parameter.
        """
        return self.highest_lowest_activities[index]

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
            and only for the selected classlist
        """
        evaluationsheets_in_range = \
            self.evaluationsheets_filter(self.startDateString(), 
                                         self.endDateString(), 
                                         None)
        return evaluationsheets_in_range


class StrengthsAndWeaknessesView(StrengthsAndWeaknessesBase, grok.View):
    """ Strengths And Weaknesses report view
    """
    grok.context(Interface)
    grok.name('strengths-and-weaknesses')
    grok.template('strengths-and-weaknesses')
    grok.require('zope2.View')

    def update(self, **kwargs):
        super(StrengthsAndWeaknessesView, self).update(**kwargs)

    def pdf_url(self):
        return '%s/%s?startdate=%s&enddate=%s' % (
            self.context.absolute_url(),
            '@@strengths-and-weaknesses-pdf',
            self.startDateString(),
            self.endDateString())


class EvaluationSheetBase(ReportViewsCommon):
    """ All base functionality for html and PDF report.
    """

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """ get classlist parameter from request, if none selected, pick first
            classlist in classlists folder.
            calculate all the activity_ids that are contained in the 
            evaluationsheets (in the selected date range).
        """
        self.classlist_uid = self.request.get('classlist_uid_selected', '')
        self.subject_uid = self.request.get('subject_topic_selected', '')
        self.language_uid = self.request.get('language_topic_selected', '')

        self.topic_filtering_on = False
        if self.subject_uid != '' or self.language_uid != '':
            self.topic_filtering_on = True     

        if self.classlist_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(self.classlists()) == 0:
                # no classlists
                self.classlist_id = ''
                return []
            else:                
                # no classlist selected so pick first one in list
                classlist = self.classlists()[0].getObject()
                self.classlist_uid = IUUID(classlist)

        # calculate the activity ids for the all the activities
        evaluationsheets_in_range = self.evaluationsheets()
        if evaluationsheets_in_range == []:
            self.activity_ids = []
            return

        all_activity_ids = []
        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            activity_ids = []
            # one ev object per learner
            for ev in evaluation_objects:
                if activity_ids == []:
                    # filter out activities based of subject and language if
                    # the filters are in use 
                    if self.topic_filtering_on:
                        activity_ids = []
                        for x in  self.valid_activities(ev.evaluation):
                            activity_ids.append(
                                [uuidToObject(ev.evaluation[x]['uid']).id,
                                 IUUID(evalsheet)])
                    else: # filtering not in use
                        # init lists so that we can use indexing
                        activity_ids = [None] * len(ev.evaluation)
                        # x iterates through the activities each learner did,
                        # if this learner was absent for this evaluation, then
                        # we obtain the activities from the next present learner
                        for x in range(len(ev.evaluation)):
                            activity_ids[x] = \
                                [uuidToObject(ev.evaluation[x]['uid']).id, 
                                 IUUID(evalsheet)]

            all_activity_ids += activity_ids

        self.activity_ids = all_activity_ids
        return 

    def activity_ids(self):
        return self.activity_ids

    def classlist(self):
        """ return select classlist """
        return uuidToObject(self.classlist_uid).Title()

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
            and only for the selected classlist
        """
        evaluationsheets_in_range = \
            self.evaluationsheets_filter(self.startDateString(), 
                                         self.endDateString(), 
                                         self.classlist_uid)
        return evaluationsheets_in_range

    def learners(self):
        """ return all of the learners from a specific classlist
        """        
        classlist = uuidToObject(self.classlist_uid)
        contentFilter = {'portal_type': 'upfront.classlist.content.learner',
                         'sort_on': 'sortable_title'}
        return classlist.getFolderContents(contentFilter)

    def scores_for_learner(self, learner):
        """ return all the scores of a learner for all the evaluationsheets in
            the specified date range.
        """
        evaluationsheets_in_range = self.evaluationsheets()

        scores = [['','']] * len(self.activity_ids)
        buckets = range(len(self.activity_ids))

        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            # one ev object per learner
            for ev in evaluation_objects:
                # only use the score data of the specified learner
                if ev.learner.to_object == learner:
                    # filter out activities based of subject and language if
                    # the filters are in use 
                    if self.topic_filtering_on:
                        activity_indexes = self.valid_activities(ev.evaluation)
                    else:
                        activity_indexes = range(len(ev.evaluation))

                    # x iterates through the activities each learner did
                    for x in activity_indexes:

                        score = ['',''] # to store eg. [u'Excellent','green']
                        score[0] = ev.evaluation[x]['rating']
                        scale = ev.evaluation[x]['rating_scale']

                        # do a color lookup for the score
                        # non-scored entries are ignored
                        if score[0] == UN_RATED:
                            pass
                        # explicitly unrated entries are ignored
                        elif score[0] == NOT_RATED:
                            pass
                        # test if activity is using zero/one custom scale
                        elif self.is_zero_one_rating_scale(scale):
                            if score[0] == 0:
                                score[1] = 'mattred'
                            elif score[0] == 1:
                                score[1] = 'mattgreen'
                        # test if activity is using default scale
                        elif self.is_standard_rating_scale(scale):
                            if score[0] == 1:
                                score[1] = 'mattred'
                            elif score[0] == 2:
                                score[1] = 'gold'
                            elif score[0] == 3:
                                score[1] = 'deepblue'
                            elif score[0] == 4:
                                score[1] = 'mattgreen'
                        # if activity is using a non-default scale
                        else:
                            colors = ['red','redorange','orange','yelloworange',    
                                      'pink','yellowgreen','pregreen','green',
                                      'bluegreen','blue','blueviolet','violet',
                                      'redviolet','brown1','brown2','brown3']
                
                            # in case someone makes a scale with 16+ ratings
                            if len(scale) > 16:
                                colors_available = [''] * len(scale)
                                colors_available[0:15] = colors
                            else:
                                colors_available = colors

                            # generate color scale for this entire activity
                            # then do color lookup based on current score
                            scale_list = []
                            for z in range(len(scale)):
                                scale_list.append(scale[z]['rating'])
                            # sort scale - we have to assume that user used 
                            # highest as the best - otherwise well the colors 
                            # not flow from red to brown as intended
                            scale_list.sort()
                            color_dict = {}
                            # assign colors to this rating scale
                            for z in range(len(scale_list)):
                                color_dict.update({scale_list[z] : 
                                                  colors_available[z]})

                            # do color lookup for the score
                            score[1] = color_dict[score[0]]

                        # translate score number (int) into a rating (string)
                        if score[0] == UN_RATED:
                            score[0] = '' # Unrated are left as blanks
                        elif score[0] == NOT_RATED:
                            score[0] = self.context.translate(_(u'Not Rated'))                            
                        else:
                            rating_scale = ev.evaluation[x]['rating_scale']
                            for y in range(len(rating_scale)):
                                if score[0] == rating_scale[y]['rating']:
                                    score[0] = rating_scale[y]['label']

                        # find correct score bucket to place this score in.
                        act_id = uuidToObject(ev.evaluation[x]['uid']).id
                        ev_id = IUUID(evalsheet)

                        notfound = True
                        idx = 0
                        while notfound:
                            if act_id == self.activity_ids[buckets[idx]][0] \
                                and ev_id == self.activity_ids[buckets[idx]][1]:
                                # found the bucket we want
                                scores[buckets[idx]] = score
                                notfound = False
                                # remove the chosen index from future searches
                                del buckets[idx]
                            else:
                                # point index at the next available bucket
                                idx += 1
        
        return [[learner.Title(),'']] + scores


class EvaluationSheetView(EvaluationSheetBase, grok.View):
    """ Evaluationsheet report view
    """
    grok.context(Interface)
    grok.name('evaluationsheet')
    grok.template('evaluationsheet')
    grok.require('zope2.View')

    def update(self, **kwargs):
        super(EvaluationSheetView, self).update(**kwargs)

    def pdf_url(self):
        return '%s/%s?classlist_uid_selected=%s&subject_topic_selected=%s&language_topic_selected=%s' % (
            self.context.absolute_url(),
            '@@evaluationsheet-pdf',
            self.classlist_uid,
            self.subject_uid,
            self.language_uid
        )


class CompositeLearnerView(grok.View, ReportViewsCommon):
    """ Composite Learner report view
    """
    grok.context(Interface)
    grok.name('compositelearner')
    grok.template('compositelearner')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """ get classlist parameter from request, if none selected, pick first
            classlist in classlists folder. 
            same for the evaluationsheet, but if none selected, pick most recent
            evaluationsheet: as provided by evaluationsheets_of_classlist method
            calculate all the activity_ids that are contained in the 
            specified evaluationsheet.
        """
        self.classlist_uid = self.request.get('classlist_uid_selected', '')
        self.evaluationsheet_uid = \
            self.request.get('evaluationsheet_uid_selected', '')

        if self.classlist_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if members_folder == None:
                return []
            if len(self.classlists()) == 0:
                # no classlists
                self.classlist_id = ''
                return []
            else:                
                # no classlist selected so pick first one in list
                classlist = self.classlists()[0].getObject()
                self.classlist_uid = IUUID(classlist)

        evaluationsheets = self.evaluationsheets_of_classlist()
        if self.evaluationsheet_uid == '':
            # this executes when one is picking a classlist with 
            # evaluatonsheets after having picked a classlist with no 
            # evaluationsheets
            if len(self.evaluationsheets_of_classlist()) == 0:
                # classlist contains no evaluationsheets
                self.evaluationsheet_uid = ''
                self.activity_ids = []
                return []
            else:                
                # no evaluationsheet selected so pick first one in list
                evalsheet = evaluationsheets[0]
                assessment = evalsheet.assessment.to_object
                if len(assessment.assessment_items) != 0:
                    self.activity_uid = \
                        IUUID(assessment.assessment_items[0].to_object)
                self.evaluationsheet_uid = IUUID(evalsheet)
        else:
            # check that the evaluationsheet selected is valid for this class
            # this check is necessary when changing classlists            
            evalsheet = uuidToObject(self.evaluationsheet_uid)
            # check if this chosen evaluationsheet is in the selected classlist 
            if not evalsheet in evaluationsheets:
                if len(evaluationsheets) != 0:
                    evalsheet = evaluationsheets[0]
                    assessment = evalsheet.assessment.to_object
                    if len(assessment.assessment_items) != 0:
                        self.activity_uid = \
                            IUUID(assessment.assessment_items[0].to_object)
                    self.evaluationsheet_uid = IUUID(evalsheet)

        # calculate the activity ids for the all the activities
        all_activity_ids = []
        contentFilter = {'portal_type': 'upfront.assessment.content.evaluation'}
        evaluation_objects = \
            [x for x in evalsheet.getFolderContents(contentFilter,
             full_objects=True)]
        activity_ids = []
        # one ev object per learner
        for ev in evaluation_objects:
            if activity_ids == []:
                # init lists so that we can use indexing
                activity_ids = [None] * len(ev.evaluation)
                # x iterates through the activities each learner did,
                # if this learner was absent for this evaluation, then
                # we obtain the activities from the next present learner
                for x in range(len(ev.evaluation)):
                    activity_ids[x] = \
                        [uuidToObject(ev.evaluation[x]['uid']).id, 
                             IUUID(evalsheet)]
        all_activity_ids += activity_ids
        self.activity_ids = all_activity_ids

    def classlist(self):
        """ return select classlist """
        return uuidToObject(self.classlist_uid).Title()

    def learners(self):
        """ return all of the learners from a specific classlist
        """        
        classlist = uuidToObject(self.classlist_uid)
        contentFilter = {'portal_type': 'upfront.classlist.content.learner',
                         'sort_on': 'sortable_title'}
        return classlist.getFolderContents(contentFilter)

    def score_for_learner(self, learner):
        """ returns the score of a learner for the a certain evaluationsheet in
            the specified classlist
            result is - name, score, percentage, rating code
        """
        evalsheet = uuidToObject(self.evaluationsheet_uid)

        score_total = 0
        activity_count = 0 # number of activities that the learner completed
        scales_total = 0
        score_percentages = [] # keeps track of learners percentage for each 
                               # activity the they completed 

        contentFilter = {'portal_type': 'upfront.assessment.content.evaluation'}
        evaluation_objects = \
            [x for x in evalsheet.getFolderContents(contentFilter,
                                                    full_objects=True)]
        # one ev object per learner
        for ev in evaluation_objects:
            # only use the score data of the specified learner
            if ev.learner.to_object == learner:
                # x iterates through the activities each learner did
                for x in range(len(ev.evaluation)):
                    score = ev.evaluation[x]['rating']
                    scale = ev.evaluation[x]['rating_scale']
                    if score not in [UN_RATED, NOT_RATED]:
                        score_total += score
                        scale_list = []
                        for z in range(len(scale)):
                            scale_list.append(scale[z]['rating'])
                        scale_list.sort()
                        # add highest possible rating from this scale
                        # to scales total
                        highest_scale_entry = scale_list[len(scale_list)-1]
                        scales_total += highest_scale_entry
                        score_percentages.append(score/highest_scale_entry)

        if scales_total != 0:
            percentage = int((score_total / scales_total)*100)
            # commented out is the mechanism that averages percentages instead
            #percentage =  \
            #    int((sum(score_percentages) / len(score_percentages))*100)
            if percentage == 100:
                rating_code = 7
            elif percentage < 100 and percentage >= 70:
                rating_code = 6
            elif percentage < 70 and percentage >= 60:
                rating_code = 5
            elif percentage < 60 and percentage >= 50:
                rating_code = 4
            elif percentage < 50 and percentage >= 40:
                rating_code = 3
            elif percentage < 40 and percentage >= 30:
                rating_code = 2
            elif percentage < 30:
                rating_code = 1
        else:
            highest_scale_entry = 'N/A'
            percentage = 'N/A'
            rating_code = '1'

        return [score_total, scales_total, percentage, rating_code]


class ClassPerformanceForActivityPDFView(grok.View, ReportViewsCommon):
    """ Class performance for a given activity PDF
    """
    grok.context(Interface)
    grok.name('classperformance-for-activity-pdf')
    grok.require('zope2.View')
    
    pdf_template = ViewPageTemplateFile('templates/classperformance-for-activity-pdf.pt')
    
    def update(self):
        self.selected_evaluationsheet = self.request['selected_evaluationsheet']
        self.selected_activity = self.request['selected_activity']

    def render(self):
        charset = self.context.portal_properties.site_properties.default_charset
        html = StringIO(self.pdf_template(view=self).encode(charset))

        # Generate the pdf
        pdf = StringIO()
        pisadoc = pisa.CreatePDF(html, pdf, raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        filename = self.__name__
        now = DT()
        nice_filename = '%s_%s' % (filename, now.strftime('%Y%m%d'))

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.pdf" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader('Last-Modified', DT.rfc822(DT()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent
    
    def make_data_uri(self):
        self.request['evaluationsheet'] = self.selected_evaluationsheet
        self.request['activity'] = self.selected_activity
        view = getMultiAdapter((self.context, self.request),
                               name='classperformance-for-activity-chart')
        data = view.get_image_data()
        return pisa.makeDataURI(data=data, mimetype='img/png')


class ClassProgressDFView(grok.View, ReportViewsCommon):
    """ Class progress PDF
    """
    grok.context(Interface)
    grok.name('classprogress-pdf')
    grok.require('zope2.View')
    
    pdf_template = ViewPageTemplateFile('templates/classprogress-pdf.pt')
    
    def update(self):
        self.classlist = self.request['classlist']
        self.startdate = self.request['startdate']
        self.enddate = self.request['enddate']
        self.subject = self.request['subject']
        self.language = self.request['language']
        self.memberid = self.request['memberid']

    def render(self):
        charset = self.context.portal_properties.site_properties.default_charset
        html = StringIO(self.pdf_template(view=self).encode(charset))

        # Generate the pdf
        pdf = StringIO()
        pisadoc = pisa.CreatePDF(html, pdf, raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        filename = self.__name__
        now = DT()
        nice_filename = '%s_%s' % (filename, now.strftime('%Y%m%d'))

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.pdf" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader('Last-Modified', DT.rfc822(DT()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent

    def make_data_uri(self):
        self.request['classlist'] = self.classlist
        self.request['startdate'] = self.startdate
        self.request['enddate'] = self.enddate
        self.request['subject'] = self.subject
        self.request['language'] = self.language

        view = getMultiAdapter((self.context, self.request),
                               name='classprogress-chart')
        data = view.get_image_data()
        return pisa.makeDataURI(data=data, mimetype='img/png')


class LearnerProgressPDFView(grok.View, ReportViewsCommon):
    """ Download the Learner Progress report as PDF. 
    """
    grok.context(Interface)
    grok.name('learnerprogress-pdf')
    grok.require('zope2.View')
    
    pdf_template = ViewPageTemplateFile('templates/learnerprogress-pdf.pt')
    
    def update(self):
        self.selected_classlist = self.request['classlist']
        self.selected_learner = self.request['learner']
        self.startdate = self.request.get('startdate', self.startDateString())
        self.enddate = self.request.get('enddate', self.endDateString())
        self.selected_subject = self.request['subject']
        self.selected_language = self.request['language']

    def render(self):
        charset = self.context.portal_properties.site_properties.default_charset
        html = StringIO(self.pdf_template(view=self).encode(charset))

        # Generate the pdf
        pdf = StringIO()
        pisadoc = pisa.CreatePDF(html, pdf, raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        filename = self.__name__
        now = DT()
        nice_filename = '%s_%s' % (filename, now.strftime('%Y%m%d'))

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.pdf" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader('Last-Modified', DT.rfc822(DT()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent
    
    def make_data_uri(self):
        self.request['classlist'] = self.selected_classlist
        self.request['learner'] = self.selected_learner
        self.request['startdate'] = self.startdate
        self.request['enddate'] = self.enddate
        self.request['subject'] = self.selected_subject
        self.request['language'] = self.selected_language

        view = getMultiAdapter((self.context, self.request),
                               name='learnerprogress-chart')
        data = view.get_image_data()
        return pisa.makeDataURI(data=data, mimetype='img/png')


class StrengthsAndWeaknessesPDFView(StrengthsAndWeaknessesBase, grok.View):
    """ Download the Strengths and Weaknesses report as PDF. 
    """
    grok.context(Interface)
    grok.name('strengths-and-weaknesses-pdf')
    grok.require('zope2.View')
    
    pdf_template = ViewPageTemplateFile('templates/strengths_and_weaknesses_as_pdf.pt')
    
    def update(self, **kwargs):
        super(StrengthsAndWeaknessesPDFView, self).update(**kwargs)

    def render(self):
        charset = self.context.portal_properties.site_properties.default_charset
        html = StringIO(self.pdf_template(view=self).encode(charset))

        # Generate the pdf
        pdf = StringIO()
        pisadoc = pisa.CreatePDF(html, pdf, raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        filename = self.__name__
        now = DT()
        nice_filename = '%s_%s' % (filename, now.strftime('%Y%m%d'))

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.pdf" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader('Last-Modified', DT.rfc822(DT()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent


class EvaluationSheetPDFView(EvaluationSheetBase, grok.View):
    """ Evaluationsheet report view
    """
    grok.context(Interface)
    grok.name('evaluationsheet-pdf')
    grok.require('zope2.View')

    pdf_template = ViewPageTemplateFile('templates/evaluationsheet-pdf.pt')
    
    def update(self, **kwargs):
        super(EvaluationSheetPDFView, self).update(**kwargs)

    def render(self):
        charset = self.context.portal_properties.site_properties.default_charset
        html = StringIO(self.pdf_template(view=self).encode(charset))

        # Generate the pdf
        pdf = StringIO()
        pisadoc = pisa.CreatePDF(html, pdf, raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        filename = self.__name__
        now = DT()
        nice_filename = '%s_%s' % (filename, now.strftime('%Y%m%d'))

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.pdf" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader('Last-Modified', DT.rfc822(DT()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent



