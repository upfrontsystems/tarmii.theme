from zope.interface import Interface, alsoProvides
from zope import schema
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobFile

from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

from tarmii.theme import MessageFactory as _

class IAssessmentItemBlobs(form.Schema):
    """ Behavior that extends the functionality of assessment item with three
        NamedBlobFile fields.
    """

    observation_sheet = NamedBlobFile(
            title=_(u"Observation Sheet"),
            required=False,
        )

    check_list = NamedBlobFile(
            title=_(u"Check list"),
            required=False,
        )

    rubric = NamedBlobFile(
            title=_(u"Rubric"),
            required=False,
        )

class IRatingFieldSchema(Interface):
    """ Schema for rating scale datagrid field, stores the label and rating
        value.
    """

    label = schema.TextLine(title=u"Label")
    rating = schema.Int(title=u"Rating")

class IRating(form.Schema):
    """ Behavior that enables each assessmentitem to set its rating scale/range.
    """

    form.fieldset('rating',
            label=u"Rating",
            fields=['rating_scale']
        )

    form.widget(rating_scale=DataGridFieldFactory)
    rating_scale = schema.List(
            title=u"Rating scale",
            value_type=DictRow(title=u"tablerow", schema=IRatingFieldSchema)
        )

alsoProvides(IAssessmentItemBlobs, IFormFieldProvider)
alsoProvides(IRating, IFormFieldProvider)
