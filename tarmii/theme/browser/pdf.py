from StringIO import StringIO
from xhtml2pdf import pisa

from five import grok
from zope.interface import Interface
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

class AssessmentPDF(grok.View):
    """ Assessment PDF view
    """
    grok.context(IAssessment)
    grok.name('assessment-pdf')
    grok.template('assessment-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = StringIO(self._render_template())

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, raise_exception=False)
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

    def activities(self):
        """ Return all the activities that this assessment references
        """
        return [x.to_object for x in self.context.assessment_items]


class SelectClasslistForEvaluationPDF(grok.View):
    """ Select Classlist for Evaluation PDF view
    """
    grok.context(IAssessment)
    grok.name('select-classlist-for-evaluationsheet-pdf')
    grok.template('select-classlist-for-evaluationsheet-pdf')
    grok.require('cmf.ModifyPortalContent')

    def classlists(self):
        """ Return all the classlists in the current user's member folder
        """
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist'}
        classlists = self.context.aq_parent.aq_parent.classlists
        return classlists.getFolderContents(contentFilter)


class EvaluationSheetPDF(grok.View):
    """ Evaluation Sheet PDF view
    """
    grok.context(IAssessment)
    grok.name('evaluationsheet-pdf')
    grok.template('evaluationsheet-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = StringIO(self._render_template())

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, raise_exception=False)
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


class ScoreSheetPDF(grok.View):
    """ Score Sheet PDF view
    """
    grok.context(IEvaluationSheet)
    grok.name('pdf')
    grok.template('scoresheet-pdf')
    grok.require('cmf.ModifyPortalContent')

    def __call__(self):
        pdf = StringIO()
        html = StringIO(self._render_template())

        # Construct a trojan horse and hide context inside it
        path = ContextString(self.context.absolute_url())
        path.context = self.context

        # Generate the pdf
        pisadoc = pisa.CreatePDF(html, pdf, path=path, raise_exception=False)
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

