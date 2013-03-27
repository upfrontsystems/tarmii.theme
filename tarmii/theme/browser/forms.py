from sets import Set
from five import grok
from zope.component.hooks import getSite
from plone.directives import dexterity
from tarmii.theme import MessageFactory as _
from tarmii.theme.interfaces import ITARMIIThemeLayer
from tarmii.theme.content.teacherresource import ITeacherResource

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

        if 'IRating.rating_scale' in Set(self.widgets.keys()):
            self.widgets['IRating.rating_scale'].field.default =\
                [{'rating': 4,
                  'label': self.context.translate(_(u'Excellent'))},
                 {'rating': 3,
                  'label': self.context.translate(_(u'Good'))},
                 {'rating': 2,
                  'label': self.context.translate(_(u'Satisfactory'))},
                 {'rating': 1,
                  'label': self.context.translate(_(u'Needs improvement'))}]

