from five import grok
from zope.interface import Interface
from plone.directives import dexterity
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')
class ReportsView(grok.View):
    """ View for reports
    """
    grok.context(Interface)
    grok.name('reports')
    grok.template('report') # using report.py and report.pt as we already have
                            # a reports folder inside browser folder
    grok.require('zope2.View')

