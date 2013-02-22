from five import grok

from plone.directives import dexterity

from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from tarmii.theme import MessageFactory as _
from tarmii.theme.interfaces import ITARMIIThemeLayer

grok.templatedir('templates')
grok.layer(ITARMIIThemeLayer)

class AssessmentItemAddForm(dexterity.AddForm):
    grok.name('upfront.assessmentitem.content.assessmentitem')
    grok.template('addassessmentitem')
    grok.layer(ITARMIIThemeLayer)

    formname = 'add-assessmentitem-form'
    kssformname = "kssattr-formname-++add++upfront.assessmentitem.content.assessmentitem"
    mainheading = _(u"Add Assessment Item")

class AssessmentItemEditForm(dexterity.EditForm):
    grok.name('edit')
    grok.context(IAssessmentItem)
    grok.template('editassessmentitem')

    formname = 'edit-patient-form'
    kssformname = "kssattr-formname-@@edit"
    mainheading = "Edit assessment item"
