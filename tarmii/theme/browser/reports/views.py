from __future__ import division
from sets import Set
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
    """ Mixin class that provides user_anonymous method and classlists method.
    """

    def user_anonymous(self):
        """ Raise Unauthorized if user is anonymous
        """
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized("You do not have permission to view this page.")

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

        evaluationsheet_uid = self.request.get('evaluationsheet', '')
        activity_uid = self.request.get('activity', '')

        # iterate through all evaluations that reference the current assessment
        activity = uuidToObject(activity_uid)

        rating_scale = {}
        count_dict = {}
        lookup_dict = {}
        for eval_obj in uuidToObject(evaluationsheet_uid).getFolderContents():
            # 1 eval_obj/learner
            for x in range(len(eval_obj.getObject().evaluation)):
                uid = eval_obj.getObject().evaluation[x]['uid']
                if activity_uid == uid:
                    # found matching activity data
                    eval_obj.getObject().evaluation[x]
                    # get the rating_scale, init the count and lookup 
                    # dictionaries only once.
                    if rating_scale == {}:
                        rating_scale = eval_obj.getObject() \
                                       .evaluation[x]['rating_scale']

                        for z in range(len(rating_scale)):
                            # init the score counter and the lookup dict
                            count_dict[rating_scale[z]['label']] = 0
                            lookup_dict[rating_scale[z]['rating']] = \
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
            # append 'learner' or 'learners' to the number of learners.
            if value > 1:
                learner_str = self.context.translate(_(u' learners'))
            else:
                learner_str = self.context.translate(_(u' learner'))
            category_labels.append(str(value) + learner_str)

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
        description = \
            self.context.translate(_(u'Number of learners per rating'))

        return { 
            'title' : title,
            'description' : description,
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
        self.classlist_uid = self.request.get('classlist_uid_selected', '')
        self.evaluationsheet_uid = \
            self.request.get('evaluationsheet_uid_selected', '')
        self.activity_uid = self.request.get('activity_uid_selected', '')

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
                classlist = members_folder.classlists.getFolderContents()[0] \
                            .getObject()
                self.classlist_uid = IUUID(classlist)

        evaluationsheets = self.evaluationsheets()
        if self.evaluationsheet_uid == '':
            # this executes when one is picking a classlist with 
            # evaluatonsheets after having picked a classlist with no 
            # evaluationsheets
            if len(self.evaluationsheets()) == 0:
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

    def evaluationsheets(self):
        """ return all of the evaluationsheets of the current classlist
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
        filtered_evalsheet_list.sort(key=lambda x: x.created)
        filtered_evalsheet_list.reverse()

        return filtered_evalsheet_list

    def activities(self):
        """ return all of the activities of a specific assessment
        """
        if self.evaluationsheet_uid == '':
            return []
        else:
            if self.evaluationsheets() == []:
                return []
            ev = uuidToObject(self.evaluationsheet_uid)
            assessment = ev.assessment.to_object
        return assessment.assessment_items

    def selected_evaluationsheet(self):
        return self.evaluationsheet_uid

    def selected_activity(self):
        return self.activity_uid    

    def getUID(self, obj):
        return IUUID(obj)

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

    def getCustomTitle(self, evaluationsheet):
        """ return title for evaluationsheet eg. 'Assessment3 on 31 May 2013'
            and translate the month part of the date
        """
        date = evaluationsheet.created()
        assessment_title = evaluationsheet.assessment.to_object.title        
        on_string = self.context.translate(_(u'on'))
        month = self.context.translate(_(date.strftime('%B')))
        date_string = '%s %s %s' % (date.day(), month, date.year())
        return assessment_title + ' ' + on_string + ' ' + date_string


class ClassProgressChartView(grok.View):
    """ Class progress for a given time period
    """
    grok.context(Interface)
    grok.name('classprogress-chart')
    grok.require('zope2.View')

    def data(self):
        # if we are here, evaluationsheets exist in the specified range

        classlist_uid = self.request.get('classlist')
        startdate = self.request.get('startdate', '')
        enddate = self.request.get('enddate', '')

        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = \
            {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets = \
            members_folder.evaluations.getFolderContents(contentFilter)

        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            cdat = obj.created().asdatetime().strftime(u'%Y-%m-%d')
            evaluationsheet_date = datetime.datetime.strptime(cdat, u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(startdate, u'%Y-%m-%d')
            end_date = datetime.datetime.strptime(enddate, u'%Y-%m-%d')
            # only include evaluationsheets for the specified class
            if obj.classlist.to_object == uuidToObject(classlist_uid):
                if evaluationsheet_date >= start_date and \
                   evaluationsheet_date <= end_date:
                    evaluationsheets_in_range.append(obj)
        
        all_scores = []
        all_learner_count = []
        all_activity_ids = []
        all_highest_ratings = []
        all_rating_scales = []
        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            scores = []
            activity_ids = []
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
                        highest_rating = [None] * len(ev.evaluation)
                        rating_scales = [None] * len(ev.evaluation)
                        number_of_learners_in_activity = len(ev.evaluation)
                    activity_ids[x] = uuidToObject(ev.evaluation[x]['uid']).id
                    # dont add unrated (0) scores into the average calculation
                    if ev.evaluation[x]['rating'] != 0:
                        # update score total and ignore explicitly "not rated"
                        if ev.evaluation[x]['rating'] != -1:
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
            all_highest_ratings += highest_rating
            all_rating_scales += rating_scales

        # filter out activities which no learners have completed
        filtered_all_highest_ratings = []
        filtered_all_scores = []
        filtered_all_activity_ids = []
        filtered_all_rating_scales = []
        filtered_all_learner_count = []
        for x in range(len(all_scores)):
            if all_learner_count[x] > 0:
                filtered_all_highest_ratings.append(all_highest_ratings[x])
                filtered_all_scores.append(all_scores[x])
                filtered_all_activity_ids.append(all_activity_ids[x])
                filtered_all_rating_scales.append(all_rating_scales[x])
                filtered_all_learner_count.append(all_learner_count[x])

        # divide the score of each activity / number of learners that completed
        # the activity
        average_all_scores = [0] * len(filtered_all_scores)
        for x in range(len(filtered_all_scores)):
            average_all_scores[x] = \
                float(filtered_all_scores[x]) / filtered_all_learner_count[x]

        # now we must normalise the average scores so that they represent valid
        # rating scale values (ie so that they fit into the rating scale)
        # eg. a value of 5.5 between valid scale values of 7 and 4, should => 4
        normalised_avg_all_scores = [0] * len(filtered_all_scores)
        for x in range(len(average_all_scores)):
            notfound = True
            rating_scale = filtered_all_rating_scales[x]
            index = 0
            while notfound:
            # we iterate through the activities rating scale (which has been
            # sorted - highest to lowest)
                if average_all_scores[x] < rating_scale[len(rating_scale)-1]:
                    # set to the lowest entry in the current rating scale,
                    # a rating average cannot be lower than this (if it is, then
                    # it is because some learners were not yet rated and thus 
                    # are marked as zero which means that practically the avg
                    # score can drop below the lowest possible score but we 
                    # correct for that here
                    normalised_avg_all_scores[x] = \
                        rating_scale[len(rating_scale)-1]
                    notfound = False
                if average_all_scores[x] == 0:
                # or lower than the lowest entry in the current rating scale 
                    # set to 0
                    normalised_avg_all_scores[x] = average_all_scores[x] 
                    notfound = False
                if rating_scale[index] <= average_all_scores[x]:
                    # the average score is bigger or equal to current scale #
                    normalised_avg_all_scores[x] = rating_scale[index]
                    notfound = False
                index += 1

        print '=========================='
        print all_scores
        print learner_count
        print all_activity_ids
        print all_highest_ratings
        print all_rating_scales
        print average_all_scores
        print normalised_avg_all_scores
        print '--------------------------'
        print filtered_all_highest_ratings
        print filtered_all_activity_ids
        print filtered_all_rating_scales
        print filtered_all_learner_count
        print filtered_all_scores
        print '=========================='

        title = self.context.translate(_(u'Class Progress'))
        max_score_legend = self.context.translate(_(u'Highest Possible Score'))
        score_legend = self.context.translate(_(u'Average Learner Score'))
        xlabel = self.context.translate(_(u'Activities'))
        ylabel = self.context.translate(_(u'Ratings'))

        return { 
            'title' : title,
            'value_data' : [
                            tuple(filtered_all_highest_ratings),
                            tuple(normalised_avg_all_scores)                           
                           ],
            'category_data' : filtered_all_activity_ids,
            'highest_score' : max(filtered_all_highest_ratings),
            'max_score_legend' : max_score_legend,
            'score_legend' : score_legend,
            'xlabel' : xlabel,
            'ylabel' : ylabel
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
                classlist = members_folder.classlists.getFolderContents()[0] \
                            .getObject()
                self.classlist_uid = IUUID(classlist)

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
            and only for the selected classlist
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = \
            {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets = \
            members_folder.evaluations.getFolderContents(contentFilter)

        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            cdat = obj.created().asdatetime().strftime(u'%Y-%m-%d')
            evaluationsheet_date = datetime.datetime.strptime(cdat, u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(self.startDateString(),
                                                    u'%Y-%m-%d')
            end_date = datetime.datetime.strptime(self.endDateString(),
                                                  u'%Y-%m-%d')
            # only include evaluationsheets for the specified class
            if obj.classlist.to_object == uuidToObject(self.classlist_uid):
                if self.check_date_integrity():
                    if evaluationsheet_date >= start_date and \
                       evaluationsheet_date <= end_date:
                        evaluationsheets_in_range.append(obj)

        return evaluationsheets_in_range

    def evaluation_objects_scored(self): 
        """ make sure that there are at least some evaluation objects that have 
            been scored in any one of the evaluationsheets in range.        
            explicitly not rated scores are regarded as not scored (as they are 
            then later not included in this line chart)
        """
        evaluationsheets_in_range = self.evaluationsheets()

        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            for ev in evaluation_objects:
                for x in range(len(ev.evaluation)):
                    if ev.evaluation[x]['rating'] > 0:
                        # a score has been found
                        return True
        return False

    def selected_classlist(self):
        return self.classlist_uid


class LearnerProgressChartView(grok.View):
    """ Learner progress for a given time period
    """
    grok.context(Interface)
    grok.name('learnerprogress-chart')
    grok.require('zope2.View')

    def data(self):
        # if we are here, evaluationsheets exist in the specified range

        classlist_uid = self.request.get('classlist', '')
        learner_uid = self.request.get('learner', '')
        startdate = self.request.get('startdate', '')
        enddate = self.request.get('enddate', '')

        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = \
           {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets = \
            members_folder.evaluations.getFolderContents(contentFilter)

        # find all evaluationsheets that match the specified date range
        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            cdat = obj.created().asdatetime().strftime(u'%Y-%m-%d')
            evaluationsheet_date = datetime.datetime.strptime(cdat, u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(startdate, u'%Y-%m-%d')
            end_date = datetime.datetime.strptime(enddate, u'%Y-%m-%d')
            # only include evaluationsheets for the specified class
            if obj.classlist.to_object == uuidToObject(classlist_uid):
                if evaluationsheet_date >= start_date and \
                   evaluationsheet_date <= end_date:
                    evaluationsheets_in_range.append(obj)
       
        all_scores = []
        all_activity_ids = []
        all_highest_ratings = []
        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            scores = []
            activity_ids = []
            highest_rating = []
            for ev in evaluation_objects:
                # only use the score data of the specified learner
                if ev.learner.to_object == uuidToObject(learner_uid):
                    if scores == []:
                        # init lists so that we can use indexing
                        scores = [0] * len(ev.evaluation) # one bucket/activity
                        activity_ids = [None] * len(ev.evaluation)
                        highest_rating = [None] * len(ev.evaluation)
                    for x in range(len(ev.evaluation)):
                        activity_ids[x] = \
                            uuidToObject(ev.evaluation[x]['uid']).id
                        scores[x] = ev.evaluation[x]['rating']
                        if scores[x] == -1:
                            # explicitly unrated (-1) scores get set to 0
                            scores[x] = 0
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
            all_highest_ratings += highest_rating

        # filter out activities which this learner has not completed
        # (unrated or "Not rated")
        filtered_all_highest_ratings = []
        filtered_all_scores = []
        filtered_all_activity_ids = []
        for x in range(len(all_scores)):
            if all_scores[x] > 0:
                filtered_all_highest_ratings.append(all_highest_ratings[x])
                filtered_all_scores.append(all_scores[x])
                filtered_all_activity_ids.append(all_activity_ids[x])

        print '=========================='
        print all_scores
        print all_activity_ids
        print all_highest_ratings
        print '--------------------------'
        print filtered_all_scores
        print filtered_all_activity_ids
        print filtered_all_highest_ratings
        print '=========================='

        title = self.context.translate(_(u'Learner Progress'))
        max_score_legend = self.context.translate(_(u'Highest Possible Score'))
        score_legend = self.context.translate(_(u'Learner Score'))
        xlabel = self.context.translate(_(u'Activities'))
        ylabel = self.context.translate(_(u'Ratings'))

        return { 
            'title' : title,
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

    def render(self):
        request = self.request
        response = request.response

        drawing = LearnerProgressChart(self.data())
        out = StringIO(renderPM.drawToString(drawing, 'PNG'))
        response.setHeader('expires', 0)
        response['content-type']='image/png'
        response['Content-Length'] = out.len
        response.write(out.getvalue())
        out.close()


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
                classlist = members_folder.classlists.getFolderContents()[0] \
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
            and only for the selected classlist
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = \
            {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets = \
            members_folder.evaluations.getFolderContents(contentFilter)

        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            cdat = obj.created().asdatetime().strftime(u'%Y-%m-%d')
            evaluationsheet_date = \
                datetime.datetime.strptime(cdat, u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(self.startDateString(),
                                                    u'%Y-%m-%d')    
            end_date = datetime.datetime.strptime(self.endDateString(),
                                                  u'%Y-%m-%d')
            # only include evaluationsheets for the specified class
            if obj.classlist.to_object == uuidToObject(self.classlist_uid):
                if self.check_date_integrity():
                    if evaluationsheet_date >= start_date and \
                       evaluationsheet_date <= end_date:
                        evaluationsheets_in_range.append(obj)

        return evaluationsheets_in_range

    def learner_has_score(self): 
        """ make sure that the selected learner has at least one scored 
            evaluation object in the selected evaluationsheets
            explicitly not rated scores are regarded as not scored (as they are 
            then later not included in this line chart)
        """
        evaluationsheets_in_range = self.evaluationsheets()

        for evalsheet in evaluationsheets_in_range:
            contentFilter = \
                {'portal_type': 'upfront.assessment.content.evaluation'}
            evaluation_objects = \
                [x for x in evalsheet.getFolderContents(contentFilter,
                                                        full_objects=True)]
            for ev in evaluation_objects:
                if ev.learner.to_object == uuidToObject(self.learner_uid):
                    for x in range(len(ev.evaluation)):
                        if ev.evaluation[x]['rating'] > 0:
                            return True
        return False
     
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
        """ calculate the two activities in which the users performed the best
            on average and the two activities in which the users performed the 
            worst on average
        """
        evaluationsheets_in_range = self.evaluationsheets()
        self.highest_lowest_activities = ['BAct1','BAct2','WAct1','WAct2']

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
            and only for the selected classlist
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = \
            {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets = \
            members_folder.evaluations.getFolderContents(contentFilter)

        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            cdat = obj.created().asdatetime().strftime(u'%Y-%m-%d')
            evaluationsheet_date = \
                datetime.datetime.strptime(cdat, u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(self.startDateString(),
                                                    u'%Y-%m-%d')    
            end_date = datetime.datetime.strptime(self.endDateString(),
                                                  u'%Y-%m-%d')
            if self.check_date_integrity():
                if evaluationsheet_date >= start_date and \
                   evaluationsheet_date <= end_date:
                    evaluationsheets_in_range.append(obj)

        return evaluationsheets_in_range

    def activity(self, index):
        """ returns an activity from the highest_lowest activities list
            activity is specified via index parameter.
        """
        return self.highest_lowest_activities[index]


class EvaluationSheetView(grok.View, ReportViewsCommon, DatePickers):
    """ Evaluationsheet report view
    """
    grok.context(Interface)
    grok.name('evaluationsheet')
    grok.template('evaluationsheet')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """ get classlist parameter from request, if none selected pick first
            classlist in classlists folder.
            calculate all the activity_ids that are contained in the 
            evaluationsheets selected by the date range.
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
                classlist = \
                    members_folder.classlists.getFolderContents()[0].getObject()
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
                    # init lists so that we can use indexing
                    activity_ids = [None] * len(ev.evaluation)
                    # x iterates through the activities each learner did
                    if len(ev.evaluation) == 0: # XXX DEBUG
                        print 'NO EVALUATION DATA!'
                    for x in range(len(ev.evaluation)):
                        activity_ids[x] = \
                            [uuidToObject(ev.evaluation[x]['uid']).id, 
                             IUUID(evalsheet)]
                elif len(ev.evaluation) > len(activity_ids):
                    # if this learner has more activities than the previous one
                    # the assumption here is that the previous learner's 
                    # activities were a subset of this learners activities. 
                    # XXX if this doesnt hold, we need to rethink our strategy.

                    # clear all previously collected activity_ids
                    activity_ids = [None] * len(ev.evaluation)
                    # use this learners activities instead
                    for x in range(len(ev.evaluation)):
                        obj = [uuidToObject(ev.evaluation[x]['uid']).id, 
                               IUUID(ev)]
                        print 'XXX DEBUG' #XXX DEBUG
                        activity_ids[x] = obj

            all_activity_ids += activity_ids
        self.activity_ids = all_activity_ids

        return 

    def evaluationsheets(self):
        """ return all user's evaluationsheets for the selected date range
            and only for the selected classlist
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        if members_folder == None:
            return []
        contentFilter = \
            {'portal_type': 'upfront.assessment.content.evaluationsheet'}
        evaluationsheets = \
            members_folder.evaluations.getFolderContents(contentFilter)

        evaluationsheets_in_range = []
        for evaluationsheet in evaluationsheets:
            obj = evaluationsheet.getObject()
            cdat = obj.created().asdatetime().strftime(u'%Y-%m-%d')
            evaluationsheet_date = \
                datetime.datetime.strptime(cdat, u'%Y-%m-%d')
            start_date = datetime.datetime.strptime(self.startDateString(),
                                                    u'%Y-%m-%d')    
            end_date = datetime.datetime.strptime(self.endDateString(),
                                                  u'%Y-%m-%d')

            # only include evaluationsheets for the specified class
            if obj.classlist.to_object == uuidToObject(self.classlist_uid):
                if self.check_date_integrity():
                    if evaluationsheet_date >= start_date and \
                       evaluationsheet_date <= end_date:
                        evaluationsheets_in_range.append(obj)

        return evaluationsheets_in_range

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
                    # x iterates through the activities each learner did

                    for x in range(len(ev.evaluation)):

                        score = ['',''] # to store eg. [u'Excellent','green']
                        score[0] = ev.evaluation[x]['rating']
                        scale = ev.evaluation[x]['rating_scale']

                        # do a color lookup for the score
                        # non-scored entries are ignored
                        if score[0] == 0:
                            pass
                        # explicitly unrated entries are ignored
                        elif score[0] == -1:
                            pass
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
                        if score[0] == 0:
                            score[0] = '' # Unrated are left as blanks
                        elif score[0] == -1:
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
                            if len(buckets) == 0:
                                print 'EMPTY !!!' # XXX debug
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

    def activity_ids(self):
        return self.activity_ids
