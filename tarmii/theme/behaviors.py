from zope.interface import alsoProvides

from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobFile

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
            title=_(u"Check List"),
            required=False,
        )

    rubric = NamedBlobFile(
            title=_(u"Rubric"),
            required=False,
        )

alsoProvides(IAssessmentItemBlobs, IFormFieldProvider)
