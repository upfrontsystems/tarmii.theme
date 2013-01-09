from smtplib import SMTPRecipientsRefused

from five.formlib.formbase import PageForm
from zope.formlib import form
from zope.interface import Interface
from zope.schema import TextLine, Text

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from zc.relation.interfaces import ICatalog

from tarmii.theme import MessageFactory as _

class IFeedbackForm(Interface):
    """ Contact us form schema
    """

    subject = TextLine(title=u'Subject',
                       description=u'Subject',
                       required=True)

    message = Text(title=_(u'Message'),
                   description=_(u'The message body'),
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

    label = msg = _(u'Contact Us')
    form_fields = form.Fields(IFeedbackForm)
    result_template = ViewPageTemplateFile('templates/feedback_result.pt')

    @form.action(_(u'send'))
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

    feedback = Text(title=_(u'Feedback'),
                   description=_(u'The message body'),
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

Topics associated with this item:
%s

"""

    label = _(u'Feedback')
    form_fields = form.Fields(IAssessmentItemFeedbackForm)
    result_template = ViewPageTemplateFile(
        'templates/assessmentitem_feedback_result.pt')

    @form.action(_(u'send'))
    def action_send(self, action, data):

        mhost = getToolByName(self.context, 'MailHost')
        pm = getToolByName(self.context, 'portal_membership')

        user_name = pm.getAuthenticatedMember().getUserName()
        user_email = pm.getAuthenticatedMember().email
        email_from = pm.email_from_address
        self.assessment_item_id = self.context.id

        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = catalog.findRelations({
            'from_id': intids.getId(self.context)})
        
        topics = ''
        notfinished = True;
        while notfinished:            
            try:
                rel = result.next()        
                if rel.to_object.portal_type == 'collective.topictree.topic':
                    topics = topics + rel.to_object.title + '\n'
            except StopIteration:
                notfinished = False;

        self.mFrom = user_name + ' <' + user_email + '>'
        self.mTo = email_from
        self.mSubject = data['subject']
        self.mBody = self.MESSAGE % (self.mFrom,
                                     self.assessment_item_id,
                                     data['subject'],
                                     data['feedback'],
                                     topics)

        try:
            mhost.send(self.mBody, self.mTo, self.mFrom, self.mSubject, 
                       immediate=True)
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused('Recipient address rejected by server')

        return self.result_template()

