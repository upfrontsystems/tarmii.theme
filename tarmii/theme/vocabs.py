from five import grok

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from tarmii.theme import MessageFactory as _

PROVINCES = SimpleVocabulary(
    [SimpleTerm(value=u'Eastern Cape', title=_(u'Eastern Cape')),
     SimpleTerm(value=u'Free State', title=_(u'Free State')),
     SimpleTerm(value=u'Gauteng', title=_(u'Gauteng')),
     SimpleTerm(value=u'Kwazulu-Natal', title=_(u'Kwazulu-Natal')),
     SimpleTerm(value=u'Limpopo', title=_(u'Limpopo')),
     SimpleTerm(value=u'Mpumalanga', title=_(u'Mpumalanga')),
     SimpleTerm(value=u'North West', title=_(u'North West')),
     SimpleTerm(value=u'Northern Cape', title=_(u'Northern Cape')),
     SimpleTerm(value=u'Western Cape', title=_(u'Western Cape'))]
    )
