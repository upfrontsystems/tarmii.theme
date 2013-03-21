from zope.i18nmessageid import MessageFactory
from plone.i18n.locales.languages import _languagelist

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('tarmii.theme')

from zope.interface import Interface
from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from plone.autoform.interfaces import OMITTED_KEY

IAssessmentItem.setTaggedValue(OMITTED_KEY,
                               [(Interface, 'introduction', 'true'),
                                (Interface, 'question', 'true'),
                                (Interface, 'answers', 'true')])

_languagelist[u'x-nso'] = {u'native' : 'Sepedi', u'name' : 'Northern Sotho'}
