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


class EvaluationSheetPDF(grok.View):
    """ Evaluation Sheet PDF view
    """
    grok.context(IEvaluationSheet)
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

    def assessment(self):
        """ Return the assessment that is associated with the current 
            evaluationsheet
        """
        return self.context.assessment.to_object

    def activities(self):
        """ Return all the activities that this evaluation sheet references
        """
        return [x.getObject() for x in 
                self.context.activities.getFolderContents()]

    def evaluations(self):
        """ Return all evaluations in the current folder
        """
        contentFilter = {
            'portal_type': 'upfront.assessment.content.evaluation'}
        return self.context.getFolderContents(contentFilter)

