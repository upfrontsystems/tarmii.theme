from five.formlib.formbase import PageForm

from zope.formlib import form
from zope.interface import Interface
from zope.schema import TextLine, Text, Choice

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class IFeedbackForm(Interface):
    """ Contact us form schema
    """

    subject = TextLine(title=u'Subject',
                       description=u'Subject',
                       required=True)

    message = Text(title=u'Message',
                   description=u'The message body',
                   required=True)
            

# use a dummy MailHost tool here to keep it simple
class MHost:
    def __init__(self):
        pass

    def Send(self, sender, to, subject, body):
        pass


class FeedbackForm(PageForm):
    """ Contact us feedback form 
    """

    label = u'Contact Us'
    form_fields = form.Fields(IFeedbackForm)
#    template = ViewPageTemplateFile('feedback_form.pt')
    result_template = ViewPageTemplateFile('templates/feedback_result.pt')

    # XXX: # The mail must be sent to the site email address configured here:
    # http://127.0.0.1:8080/Plone/@@mail-controlpanel
    # The mail must include the user's name and email in addition to the subject 
    # and message capture on the form.

    @form.action("send")
    def action_send(self, action, data):
        mhost = MHost()
        mt = getToolByName(self.context, 'portal_membership')
        user_name = mt.getAuthenticatedMember().getUserName()
        user_email = mt.getAuthenticatedMember().email
        self.mFrom = user_name + ' (' + user_email + ')'
        self.mTo = "feedback@mycompany.com"
        self.mSubject = data['subject']
        self.mBody = data['message']
        mhost.Send(self.mFrom, self.mTo, self.mSubject, self.mBody)
        return self.result_template()
