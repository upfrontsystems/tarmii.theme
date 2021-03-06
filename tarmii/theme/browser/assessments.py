from five import grok
from zope.interface import Interface
from plone.directives import dexterity
from tarmii.theme import MessageFactory as _
from Products.CMFPlone.PloneBatch import Batch

grok.templatedir('templates')

class AssessmentsView(grok.View):
    """ View for assessment folders
    """
    grok.context(Interface)
    grok.name('assessments')
    grok.template('assessments')
    grok.require('zope2.View')

    def assessments(self):
        """ Return all the classlists in the current folder
        """
        contentFilter = {
            'portal_type': 'upfront.assessment.content.assessment'}
        return self.context.getFolderContents(contentFilter)

    def assessments_batch(self):
        """ Return assessments in the current folder.
            Return batched.
        """
        b_size = 10
        b_start = self.request.get('b_start', 0)
        return Batch(self.assessments(), b_size, int(b_start), orphan=0)

    def add_assessment_url(self):
        """ URL for assessment add form
        """
        return "%s/++add++upfront.assessment.content.assessment" % (
            self.context.absolute_url())

    def translated_date(self, date):
        """ Translate the month part of the date
        """
        month = self.context.translate(_(date.strftime('%B')))
        return '%s %s %s' % (date.day(), month, date.year())
