from sets import Set
from five import grok
from zope import schema
from zope.component import getUtility
from zope.interface import Interface, alsoProvides, Invalid
from z3c.form import validator
from z3c.relationfield.schema import RelationChoice, RelationList

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.namedfile.field import NamedBlobFile
from Products.CMFCore.utils import getToolByName

from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

from upfront.assessmentitem.behaviors import IMarks, IResponseTime
from upfront.classlist.content.classlist import IClassList

from tarmii.theme.browser.topicswidget import TopicsFieldWidget
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


class ITopicTags(form.Schema):
    """ Behavior that enables tagging content with topics in a topic
        tree, using a custom TopicsWidget
    """

    form.widget(topics=TopicsFieldWidget)
    topics = RelationList(
        default=[],
        value_type=RelationChoice(title=_(u"Related"),
                                  source=ObjPathSourceBinder(
                                  object_provides=
                                      'collective.topictree.topic.ITopic')
                                  ),
        required=False,
    )


class IItemMetadata(ITopicTags):
    """ Combine extra activity fields with ITopicTags
    """

    form.fieldset(
        'categorization',
        label=_(u'Categorization'),
        fields=['topics'],
        )

    dexterity.write_permission(item_id='cmf.ManagePortal')
    item_id = schema.TextLine(
            title=_(u"Item ID"),
            required=False,
        )

    activity = RichText(
            title=_(u"Learner Task/Activity"),
            required=True,
        )

    content_concept_skills = RichText(
            title=_(u"Content/Concept/Skills Assessed"),
            required=False,
        )

    prior_knowledge_skills = RichText(
            title=_(u"Prior Knowledge or Skill(s) Assessed"),
            required=False,
        )

    equipment_and_administration = RichText(
            title=_(u"Equipment and Administration (For the teacher)"),
            required=False,
        )


class IFilterSelect(form.Schema):
    """ Behavior that enables a topic tree to select on which content types it 
        is to be used. At the moment we have two options Activities and Teacher
        Resources.
    """

    use_with_activities = schema.Bool(
            title=_(u"Use with Activities"),
            default=False,
            required=True,
        )

    use_with_resources = schema.Bool(
            title=_(u"Use with Teacher Resources"),
            default=False,
            required=True,
        )


alsoProvides(IAssessmentItemBlobs, IFormFieldProvider)
alsoProvides(IRating, IFormFieldProvider)
alsoProvides(ITopicTags, IFormFieldProvider)
alsoProvides(IItemMetadata, IFormFieldProvider)
alsoProvides(IFilterSelect, IFormFieldProvider)


class RatingValidator(validator.SimpleFieldValidator):
    
    def validate(self, value):
        super(RatingValidator, self).validate(value)

        ratings_set = Set([])
        for x in range(len(value)):
            rating = value[x]['rating']            
            if rating < 0:
                raise Invalid(_(u"All rating values must be positive or " +\
                                u"equal to zero"))
            if rating in ratings_set:
                raise Invalid(_(u"All rating values must be unique"))
            else:
                ratings_set.add(rating)
      

validator.WidgetValidatorDiscriminators(RatingValidator,
                                        field=IRating['rating_scale'])
grok.global_adapter(RatingValidator)

class ItemIdValidator(validator.SimpleFieldValidator):
    
    def validate(self, value):
        super(ItemIdValidator, self).validate(value)

        # check that id is unique 
        # (all ids when created are URLNormalized)
        normalizer = getUtility(IURLNormalizer)
        normalized_value = normalizer.normalize(value)
        pc = getToolByName(self.context, 'portal_catalog')
        query = {
            "portal_type" : "upfront.assessmentitem.content.assessmentitem",
            "item_id": normalized_value,
        }
        brains = pc(query)
        # If we find one with the same item_id it could just be the object we
        # are editing, in which case we don't have to worry, it is legit.
        if len(brains) == 1 and brains[0].getObject() == self.context:
            return

        if len(brains) > 0:
            raise Invalid(_(u"This Item ID is already in use"))
      

validator.WidgetValidatorDiscriminators(ItemIdValidator,
                                        field=IItemMetadata['item_id'])
grok.global_adapter(ItemIdValidator)


