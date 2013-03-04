from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('tarmii.theme')

from zope.interface import Interface
from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from plone.autoform.interfaces import OMITTED_KEY

IAssessmentItem.setTaggedValue(OMITTED_KEY,
                               [(Interface, 'introduction', 'true'),
                                (Interface, 'question', 'true'),
                                (Interface, 'answers', 'true')])
