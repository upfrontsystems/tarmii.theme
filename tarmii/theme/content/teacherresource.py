from five import grok

from zope.interface import Interface
from plone.directives import dexterity, form
from plone.namedfile.field import NamedBlobFile

from tarmii.theme import MessageFactory as _

class ITeacherResource(form.Schema):
    """ Description of TeacherResource content type
    """

    resource = NamedBlobFile(
            title=_(u"Resource File"),
            required=True,
        )

class TeacherResource(dexterity.Item):
    grok.implements(ITeacherResource)
