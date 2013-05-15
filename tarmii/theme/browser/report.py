from five import grok
from zope.interface import Interface
from plone.directives import dexterity

grok.templatedir('templates')
class ReportsView(grok.View):
    """ View for reports
    """
    grok.context(Interface)
    grok.name('reports')
    # using report.py and report.pt instead of 
    # reports.pyas we already have a reports
    # folder inside tarmii.theme.browser folder
    grok.template('report') 
    grok.require('zope2.View')
