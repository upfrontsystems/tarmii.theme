from sets import Set
from five import grok
from zope.interface import Interface, alsoProvides, Invalid
from zope import schema
from z3c.form import validator
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

    label = schema.TextLine(title=_(u"Label"))
    rating = schema.Int(title=_(u"Rating"))

class IRating(form.Schema):
    """ Behavior that enables each assessmentitem to set its rating scale/range.
    """

    form.fieldset('rating',
            label=_(u"Rating"),
            fields=['rating_scale']
        )

    form.widget(rating_scale=DataGridFieldFactory)
    rating_scale = schema.List(
            title=_(u"Rating scale"),
            value_type=DictRow(title=u"tablerow", schema=IRatingFieldSchema),
            default= [{'rating': 4, 'label': _(u'Excellent')},
                      {'rating': 3, 'label': _(u'Good')},
                      {'rating': 2, 'label': _(u'Satisfactory')},
                      {'rating': 1, 'label': _(u'Needs improvement')}]
        )


alsoProvides(IAssessmentItemBlobs, IFormFieldProvider)
alsoProvides(IRating, IFormFieldProvider)


class RatingValidator(validator.SimpleFieldValidator):
    
    def validate(self, value):
        super(RatingValidator, self).validate(value)

        ratings_set = Set([])
        for x in range(len(value)):
            rating = value[x]['rating']            
            if rating <= 0:
                raise Invalid(_(u"All rating values must be positive and\
                                 larger than zero."))
            if rating in ratings_set:
                raise Invalid(_(u"All rating values must be unique."))
            else:
                ratings_set.add(rating)
      

validator.WidgetValidatorDiscriminators(RatingValidator,
                                        field=IRating['rating_scale'])
grok.global_adapter(RatingValidator)


