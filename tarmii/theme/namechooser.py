from five import grok
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from plone.app.content.namechooser import NormalizingNameChooser

from Acquisition import aq_base
from Products.CMFCore.interfaces import IFolderish

from upfront.assessmentitem.content.assessmentitemcontainer import \
    IAssessmentItemContainer
from tarmii.theme.interfaces import IItemVersion   

class AssessmentItemNameChooser(grok.Adapter, NormalizingNameChooser):
    """ Use the IItemVersion utility to assign a version number as the
        assessment item's name
    """
    grok.implements(INameChooser)
    grok.context(IFolderish)

    def chooseName(self, name, object):
        if not IAssessmentItemContainer.providedBy(object):
            return super(AssessmentItemNameChooser, self).chooseName(
                name, object)
        else:
            utility = getUtility(IItemVersion)
            if not name:
                # first check if object has an id
                name = getattr(aq_base(object), 'id', None)
                if not name:
                    name = 'Q%03d' % utility.next_version()

            return name
