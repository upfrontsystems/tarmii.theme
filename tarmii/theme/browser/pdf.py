import unicodedata
from DateTime import DateTime
from StringIO import StringIO
from xhtml2pdf import pisa

from five import grok
from zope.interface import Interface
from zope.component.hooks import getSite
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName

from upfront.assessment.content.assessment import IAssessment
from upfront.assessment.content.evaluationsheet import IEvaluationSheet
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

# This is an extended String class that contains a context attribute. The idea
# is to pass our context on this attribute, so that our patched pisa can
# use/abuse it.
class ContextString(str):
    context = None

class ActivitiesPDF(grok.View):
    """ Activities PDF view
    """
    grok.context(Interface)
    grok.name('activities-pdf')
    grok.template('activities-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = self._render_template()
        html = StringIO(html.encode('utf-8'))

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, encoding='utf-8',
                                 raise_exception=False)
        
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        now = DateTime()
        nice_filename = '%s_%s' % ('activities', now.strftime('%Y%m%d'))
        self.request.response.setHeader("Content-Disposition",
                                            "attachment; filename=%s.pdf" % 
                                             nice_filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent

    def activities(self):
        """ Return all the activities that this assessment references
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type=\
                                'upfront.assessmentitem.content.assessmentitem',
                                sort_on='id')
        return [x.getObject() for x in brains]

    def topics(self, activity):
        """ Return the categorization for a specific activity
        """
        if hasattr(activity,'topics'):
            return [x.to_object.title for x in activity.topics]
        return ''

    def rating_scale(self, activity):
        """ Return the rating scale for a specific activity
        """
        scale_str = ''
        for x in range(len(activity.rating_scale)):
            scale_str = scale_str + str(activity.rating_scale[x]['label']) +\
                        ' = ' + str(activity.rating_scale[x]['rating']) + ', '
        return scale_str


class AssessmentPDF(grok.View):
    """ Assessment PDF view
    """
    grok.context(IAssessment)
    grok.name('assessment-pdf')
    grok.template('assessment-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = self._render_template()
        html = StringIO(html.encode('utf-8'))

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, encoding='utf-8',
                                 raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=assessment-%s.pdf" 
                                         % self.context.id)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent

    def activities(self):
        """ Return all the activities that this assessment references
        """
        return [x.to_object for x in self.context.assessment_items]

    def school_name(self):
        """ Return the school name of the current logged in teacher
        """
        pm = getToolByName(self.context, 'portal_membership')
        return pm.getAuthenticatedMember().getProperty('school')

    def topictrees(self):
        """ Return all the topic trees that are used for tagging activities
            Only return Grade and Term if present
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_activities:
                if x.id in ['grade', 'term']:
                    topictree_list.append(x.getObject())
        return topictree_list

    def topics(self, topictree):
        """ Return the topics of the activities that this assessment 
            references, only return the ones matching the specified topictree
        """
        activities = [x.to_object for x in self.context.assessment_items]
        topic_list = []

        for activity in activities:
            if hasattr(activity,'topics'):
                topics = activity.topics
                for topic in topics:
                    if topic.to_object.aq_parent.id == topictree.id:
                        if topic.to_object.title not in topic_list:
                            # convert to string from unicode if necessary
                            if isinstance(topic.to_object.title, unicode):    
                                topic_string = unicodedata.normalize('NFKD',
                                 topic.to_object.title).encode('ascii','ignore')
                                topic_list.append(topic_string)
                            else:
                                topic_list.append(topic.to_object.title)

        return ', '.join(map(str,topic_list))


class SelectClasslistForEvaluationPDF(grok.View):
    """ Select Classlist for Evaluation PDF view
    """
    grok.context(IAssessment)
    grok.name('select-classlist-for-evaluationsheet-pdf')
    grok.template('select-classlist-for-evaluationsheet-pdf')
    grok.require('cmf.ModifyPortalContent')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):

        if self.request.form.has_key('buttons.select.classlist.submit'):
            classlist_uid = self.request['classlist_uid_selected']
            # Redirect to evaluationsheet pdf
            url = '%s/@@evaluationsheet-pdf?classlist_uid_selected=%s' %\
                  (self.context.absolute_url(),classlist_uid)
            return self.request.RESPONSE.redirect(url)

        if self.request.form.has_key('buttons.select.classlist.cancel'):
            # Redirect to the assessments listing
            url = self.context.aq_parent.absolute_url()
            return self.request.RESPONSE.redirect(url)

    def classlists(self):
        """ Return all the classlists in the current user's member folder
        """
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist'}
        classlists = self.context.aq_parent.aq_parent.classlists
        return classlists.getFolderContents(contentFilter)

    def evaluation_sheet_pdf_path(self):
        return '%s/@@evaluationsheet-pdf' % self.context.absolute_url()

    def view_url(self):
        return '%s/select-classlist-for-evaluationsheet-pdf' %\
               self.context.absolute_url()


class EvaluationSheetPDF(grok.View):
    """ Evaluation Sheet PDF view
    """
    grok.context(IAssessment)
    grok.name('evaluationsheet-pdf')
    grok.template('evaluationsheet-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = self._render_template()
        html = StringIO(html.encode('utf-8'))

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, encoding='utf-8',
                                 raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=evaluation-%s.pdf"
                                         % self.context.id)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent

    def assessment_title(self):
        return self.context.Title()

    def activities(self):
        """ Return all the activities in this  evaluations in the current folder
        """
        return [x.to_object for x in self.context.assessment_items]

    def learners(self):    
        """ Return all learners for the selected classlist
        """

        classlist_uid = self.request['classlist_uid_selected']
        classlist = uuidToObject(classlist_uid)
        contentFilter = {'portal_type': 'upfront.classlist.content.learner',
                         'sort_on': 'sortable_title'}

        return [x.getObject() for x in\
                                     classlist.getFolderContents(contentFilter)]


class ScoreSheetPDF(grok.View):
    """ Score Sheet PDF view
    """
    grok.context(IEvaluationSheet)
    grok.name('pdf')
    grok.template('scoresheet-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = self._render_template()
        html = StringIO(html.encode('utf-8'))

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, encoding='utf-8',
                                 raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.pdf" % 
                                         self.context.id)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent

    def assessment(self):
        """ Return the assessment that is associated with the current 
            evaluationsheet
        """
        return self.context.assessment.to_object

    def learners(self):
        """ return all of the learners from a specific classlist
        """        
        classlist = self.context.classlist.to_object
        contentFilter = {'portal_type': 'upfront.classlist.content.learner',
                         'sort_on': 'sortable_title'}
        return classlist.getFolderContents(contentFilter)

    def scores_for_learner(self, learner):
        """ return all the scores of a learner for all the evaluationsheets in
            the specified date range.
        """
        activity_ids = self.activity_ids()

        scores = [''] * len(activity_ids)
        buckets = range(len(activity_ids))

        evalsheet = self.context
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

                    # translate score number (int) into a rating (string)
                    if score == 0:
                        score = '' # Unrated are left as blanks
                    elif score == -1:
                        score = self.context.translate(_(u'Not Rated'))                            
                    else:
                        rating_scale = ev.evaluation[x]['rating_scale']
                        for y in range(len(rating_scale)):
                            if score == rating_scale[y]['rating']:
                                score = rating_scale[y]['label']

                    # find correct score bucket to place this score in.
                    act_id = uuidToObject(ev.evaluation[x]['uid']).id

                    notfound = True
                    idx = 0
                    while notfound:
                        if act_id == activity_ids[buckets[idx]]:
                            # found the bucket we want
                            scores[buckets[idx]] = score
                            notfound = False
                            # remove the chosen index from future searches
                            del buckets[idx]
                        else:
                            # point index at the next available bucket
                            idx += 1
        
        return [learner.Title()] + scores

    def activity_ids(self):
        """ get the activity ids for the activities in this current 
            evaluationsheet
        """        
        assessment = self.context.assessment.to_object
        activity_ids = [ x.to_object.id for x in assessment.assessment_items ]
        return activity_ids


class TeacherInformationPDF(grok.View):
    """ Teacher Information PDF view
    """
    grok.context(IAssessment)
    grok.name('teacher-info-pdf')
    grok.template('teacher-info-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = self._render_template()
        html = StringIO(html.encode('utf-8'))

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, encoding='utf-8',
                                 raise_exception=False)
        assert pdf.len != 0, 'Pisa PDF generation returned empty PDF!'
        html.close()
        pdfcontent = pdf.getvalue()
        pdf.close()

        self.request.response.setHeader("Content-Disposition",
                                       "attachment; filename=teacherinfo-%s.pdf" 
                                        % self.context.id)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdfcontent))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdfcontent)
        return pdfcontent


    def activities(self):
        """ Return all the activities that this assessment references
        """
        return [x.to_object for x in self.context.assessment_items]

    def school_name(self):
        """ Return the school name of the current logged in teacher
        """
        pm = getToolByName(self.context, 'portal_membership')
        return pm.getAuthenticatedMember().getProperty('school')

    def topictrees(self):
        """ Return all the topic trees that are used for tagging activities
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_activities:
                topictree_list.append(x.getObject())
        return topictree_list

    def topics(self, topictree):
        """ Return the topics of the activities that this assessment 
            references, only return the ones matching the specified topictree
        """
        activities = [x.to_object for x in self.context.assessment_items]
        topic_list = []

        for activity in activities:
            if hasattr(activity,'topics'):
                topics = activity.topics
                for topic in topics:
                    if topic.to_object.aq_parent.id == topictree.id:
                        if topic.to_object.title not in topic_list:
                            # convert to string from unicode if necessary
                            if isinstance(topic.to_object.title, unicode):    
                                topic_string = unicodedata.normalize('NFKD',
                                 topic.to_object.title).encode('ascii','ignore')
                                topic_list.append(topic_string)
                            else:
                                topic_list.append(topic.to_object.title)

        return ', '.join(map(str,topic_list))

    def topic_per_topictree(self, activity, topictree):
        """ Return the topic given an activity and topictree
        """
        # if activity has topics, place in correct positions in the topic list
        if hasattr(activity,'topics'):
            for topic in activity.topics:
                if topic.to_object.aq_parent.id == topictree.id:
                    return topic.to_object.title

        return ''

    def assessment_date(self):
        """ Return date that assessment was created with month translated
        """

        day = self.context.created().day()
        month = self.context.translate(_(self.context.created().strftime('%B')))
        year = self.context.created().year()
        return '%s %s %s' % (day, month, year)


