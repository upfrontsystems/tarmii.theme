from StringIO import StringIO
from reportlab.graphics import renderPM

from five import grok
from zope.app.intid.interfaces import IIntIds
from zope.component.hooks import getSite
from zope.component import getUtility
from zope.interface import Interface
from zc.relation.interfaces import ICatalog
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName


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

        for evalsheet in members_folder.evaluations.getFolderContents():
            if evalsheet.getObject() in evalsheet_rel_list:
                rating_scale = {}
                count_dict = {}
                lookup_dict = {}
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
                            # do not add unrated (0) entries into the count
                            if rating != 0:
                               count_dict[lookup_dict[rating]] += 1



        return { 
            'title' : 'Class performance for activity',
            'value_labels'   : (
                ('excellent', 'Excellent'),
                ('good', 'Good'),
                ('satisfactory', 'Satisfactory'),
                ('needsimprovement', 'Needs improvement')),
            'value_data' : (88, 6, 5, 1)
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
        """ store the of the request parameters, if they are '',
            initialise them in an intelligent manner to first choices of the 
            options (if applicable)
        """
        self.assessment_uid = self.request.get('assessment_uid_selected', '')
        self.activity_uid = self.request.get('activity_uid_selected', '')

        if self.assessment_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
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

    def assessments(self):
        """ return all of the assessments of the current user
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
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

