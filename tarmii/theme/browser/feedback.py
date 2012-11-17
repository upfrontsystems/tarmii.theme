from smtplib import SMTPRecipientsRefused

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
            

class FeedbackForm(PageForm):
    """ Contact us feedback form 
    """

    MESSAGE = u"""
    Message from user: %s

    Subject: %s
    Message:

    %s

    """

    label = u'Contact Us'
    form_fields = form.Fields(IFeedbackForm)
    result_template = ViewPageTemplateFile('templates/feedback_result.pt')

    @form.action("send")
    def action_send(self, action, data):

        mhost = getToolByName(self.context, 'MailHost')
        pm = getToolByName(self.context, 'portal_membership')

        user_name = pm.getAuthenticatedMember().getUserName()
        user_email = pm.getAuthenticatedMember().email
        email_from = pm.email_from_address

        self.mFrom = user_name + ' <' + user_email + '>'
        self.mTo = email_from
        self.mSubject = data['subject']
        self.mBody = self.MESSAGE % (self.mFrom,
                                     data['subject'],
                                     data['message'])

        try:
            mhost.send(self.mBody, self.mTo, self.mFrom, self.mSubject, 
                       immediate=True)
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused('Recipient address rejected by server')

        return self.result_template()


class IAssessmentItemFeedbackForm(Interface):
    """ Assessment Item Feedback form schema
    """

    subject = TextLine(title=u'Subject',
                       description=u'Subject',
                       required=True)

    feedback = Text(title=u'Feedback',
                   description=u'The message body',
                   required=True)


class AssessmentItemFeedbackForm(PageForm):
    """ Assessment Item feedback form 
    """

    MESSAGE = u"""
    Message from user: %s
    regarding item: %s

    Subject: %s
    Message:

    %s

    """

    label = u'Feedback'
    form_fields = form.Fields(IAssessmentItemFeedbackForm)
    result_template = ViewPageTemplateFile(
        'templates/assessmentitem_feedback_result.pt')

    @form.action("send")
    def action_send(self, action, data):

        mhost = getToolByName(self.context, 'MailHost')
        pm = getToolByName(self.context, 'portal_membership')

        user_name = pm.getAuthenticatedMember().getUserName()
        user_email = pm.getAuthenticatedMember().email
        email_from = pm.email_from_address
        self.assessment_item_id = self.context.id

        self.mFrom = user_name + ' <' + user_email + '>'
        self.mTo = email_from
        self.mSubject = data['subject']
        self.mBody = self.MESSAGE % (self.mFrom,
                                     self.assessment_item_id,
                                     data['subject'],
                                     data['feedback'])

        try:
            mhost.send(self.mBody, self.mTo, self.mFrom, self.mSubject, 
                       immediate=True)
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused('Recipient address rejected by server')

        return self.result_template()

