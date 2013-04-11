from five import grok
from zope.interface import Interface
from plone.directives import dexterity
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

    def add_assessment_url(self):
        """ URL for assessment add form
        """
        return "%s/++add++upfront.assessment.content.assessment" % (
            self.context.absolute_url())

    def translated_date(self, date):
        """ Translate the month part of the date
        """
        month = self.context.translate(date.strftime('%B'))
        return '%s %s %s' % (date.day(), month, date.year())
