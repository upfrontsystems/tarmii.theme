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

    def activities(self):
        """ Return all the activities that this evaluation sheet references
        """
        return [x.to_object for x in 
                self.context.assessment.to_object.assessment_items]

    def evaluations(self):
        """ Return all evaluations in the current folder
        """
        contentFilter = {'portal_type': 'upfront.assessment.content.evaluation'}
        return self.context.getFolderContents(contentFilter)

    def evaluation_data(self):
        """ For each activity return the learners being evaluated and their 
            score, sorted by activity 1,2,3 etc.
        """
        data = []
        activity_entry = []
        # for each activity
        activities = self.context.assessment.to_object.assessment_items
        for x in range(len(activities)):
            # for each learner
            activity_entry = []
            for lrnr in range(len(self.context.getFolderContents())):
                evaluation = self.context.getFolderContents()[lrnr].getObject()
                activity_entry.append(
                    {'learner': evaluation.learner.to_object.Title(),
                     'rating' : evaluation.evaluation[x]['rating'],
                     'rating_scale' : activities[x].to_object.rating_scale
                    })
            data.append(activity_entry)
            activity_entry = []

        return data


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

    def topics_per_topictree(self, topictree):
        """ For each topictree, check which activities in the assessment
            use the provided topictree and return which topic they were tagged
            with. eg. for Language topictree with 4 activities in an assessment:
            this method will return ['English', "Xhosa', '', 'English'] for
            instance.
        """

        topictrees = self.topictrees()
        activities = self.activities()

        # init a blank topic list
        topic_list = []
        for x in range(len(activities)):
            topic_list.append('')

        # if activity has topics, place in correct positions in the topic list
        for activity_index in range(len(activities)):
            activity = activities[activity_index]
            if hasattr(activity,'topics'):
                for x in range(len(topictrees)):
                    for topic in activity.topics:
                        if topic.to_object.aq_parent.id == topictree.id:
                            topic_list[activity_index] = topic.to_object.title

        return topic_list

