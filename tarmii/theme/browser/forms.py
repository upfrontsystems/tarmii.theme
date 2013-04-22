import datetime
from sets import Set
from five import grok
from zope.component import getUtility
from zope.component.hooks import getSite
from plone.directives import dexterity
from Products.CMFCore.utils import getToolByName

from tarmii.theme import MessageFactory as _
from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme.content.teacherresource import ITeacherResource
from upfront.assessment.content.assessment import IAssessment
from upfront.classlist.content.classlist import IClassList
from upfront.pagetracker.interfaces import IPageTracker
from upfront.pagetracker.browser.viewlets import PageTrackingViewlet

grok.templatedir('templates')
grok.layer(ITARMIIThemeLayer)

class TeacherResourceAddForm(dexterity.AddForm):
    grok.name('tarmii.theme.content.teacherresource')
    grok.layer(ITARMIIThemeLayer)

    def nextURL(self):
        # both save and cancel buttons redirect to the same place
        site = getSite()
        return '%s/resources' % (site.absolute_url())


class TeacherResourceEditForm(dexterity.EditForm):
    grok.name('edit')
    grok.context(ITeacherResource)

    def nextURL(self):
        # both save and cancel buttons redirect to the same place
        site = getSite()
        return '%s/resources' % (site.absolute_url())


class ActivityAddForm(dexterity.AddForm):
    grok.name('upfront.assessmentitem.content.assessmentitem')
    grok.layer(ITARMIIThemeLayer)

    def updateWidgets(self):
        """ Customize widget options before rendering the form. """
        super(ActivityAddForm, self).updateWidgets()

        for x in range(len(self.groups)):
            if 'IRating.rating_scale' in Set(self.groups[x].fields.keys()):            
                self.groups[x].fields['IRating.rating_scale'].field.default =\
                    [{'rating': 4,
                      'label': self.context.translate(_(u'Excellent'))},
                     {'rating': 3,
                      'label': self.context.translate(_(u'Good'))},
                     {'rating': 2,
                      'label': self.context.translate(_(u'Satisfactory'))},
                     {'rating': 1,
                      'label': self.context.translate(_(u'Needs improvement'))}]


class CustomLogger:
    """ Mixin class that provides custom log_url method.
    """

    def log_url(self):
        """ Log data from current request with page tracker
            (same as update method of PageTrackerViewlet)
        """
        mt = getToolByName(self.context, 'portal_membership')
        user = mt.getAuthenticatedMember().getUserName()
        now = datetime.datetime.now()
        datetime_str = now.strftime('%d/%m/%Y %H:%M:%S')

        data = { "time" : datetime_str,
                 "url"  : self.request['URL'],
                 "user" : user }

        pagetracker = getUtility(IPageTracker)
        pagetracker.log(data)


class ClassListAddForm(CustomLogger, dexterity.AddForm):
    grok.name('upfront.classlist.content.classlist')
    grok.template('addclasslist')
    grok.layer(ITARMIIThemeLayer)

    label = ''
    formname = 'form'
    kssformname = "kssattr-formname-++add++upfront.classlist.content.classlist"

    def mainheading(self):
        return self.context.translate(_("Add Classlist"))


class ClassListEditForm(CustomLogger, dexterity.EditForm):
    grok.name('edit')
    grok.context(IClassList)
    grok.template('editclasslist')

    formname = 'form'
    kssformname = "kssattr-formname-@@edit"

    def mainheading(self):
        return self.context.translate(_("Edit Classlist"))


class AssessmentAddForm(CustomLogger, dexterity.AddForm):
    grok.name('upfront.assessment.content.assessment')
    grok.template('addclasslist') # reusing addclasslist as form is the same
    grok.layer(ITARMIIThemeLayer)

    label = ''
    formname = 'form'
    kssformname= "kssattr-formname-++add++upfront.assessment.content.assessment"

    def mainheading(self):
        return self.context.translate(_("Add Assessment"))


class AssessmentEditForm(CustomLogger, dexterity.EditForm):
    grok.name('edit')
    grok.context(IAssessment)
    grok.template('editclasslist') # reusing editclasslist as form is the same

    formname = 'form'
    kssformname = "kssattr-formname-@@edit"

    def mainheading(self):
        return self.context.translate(_("Edit Assessment"))


class AssessmentEvaluationSheetAddForm(CustomLogger, dexterity.AddForm):
    grok.name('upfront.assessment.content.evaluationsheet')
    grok.template('addevaluationsheet')
    grok.layer(ITARMIIThemeLayer)

    label = ''
    formname = 'form'
    kssformname =\
            "kssattr-formname-++add++upfront.assessment.content.evaluationsheet"

    def mainheading(self):
        return self.context.translate(_("Add EvaluationSheet"))

