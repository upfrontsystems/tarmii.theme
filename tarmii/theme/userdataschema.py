from zope import schema
from zope.interface import implements
from zope.schema import TextLine
from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchema
from tarmii.theme.vocabs import PROVINCES
from tarmii.theme import MessageFactory as _

class ITARMIIUserDataSchema(IUserDataSchema):

    teacher_mobile_number = schema.TextLine(
            title=_(u"Cell Phone Number"),
            required=True,
        )

    school = schema.TextLine(
            title=_(u"School"),
            required=True,
        )

    province = schema.Choice(
            title=_(u"Province"),
            required=True,
            vocabulary=PROVINCES,
        )

    EMIS = schema.TextLine(
            title=_(u"EMIS"),
            required=True,
        )

    school_contact_number = schema.TextLine(
            title=_(u"School Contact Number"),
            required=True,
        )

    school_email = schema.TextLine(
            title=_(u"School Email"),
            required=True,
        )

    qualification = schema.TextLine(
            title=_(u"Qualification"),
            required=True,
        )

    years_teaching = schema.TextLine(
            title=_(u"Number of years teaching foundation phase"),
            required=True,
        )

    uuid = schema.TextLine(
            title=_(u"UUID"),
        )

class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        return ITARMIIUserDataSchema
