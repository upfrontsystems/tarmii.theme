from five import grok
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from plone.app.content.namechooser import NormalizingNameChooser
from plone.i18n.normalizer.interfaces import IURLNormalizer

from Acquisition import aq_base
from Products.CMFCore.interfaces import IFolderish

from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from upfront.assessment.content.evaluationsheet import IEvaluationSheet
from tarmii.theme.interfaces import IItemVersion   

class AssessmentItemNameChooser(grok.Adapter, NormalizingNameChooser):
    """ Use the IItemVersion utility to assign a version number as the
        assessment item's name
    """
    grok.implements(INameChooser)
    grok.context(IFolderish)

    def chooseName(self, name, object):

        # AssessmentItem
        if IAssessmentItem.providedBy(object):
            normalizer = getUtility(IURLNormalizer)
            # check if admin user specified a custom item_id
            if hasattr(object, 'item_id'):
                if object.item_id is not None:
                    return normalizer.normalize(str(object.item_id))

            # otherwise generate a name using ItemVersion utilty
            utility = getUtility(IItemVersion)
            if not name:
                # first check if object has an id
                name = getattr(aq_base(object), 'id', None)
                if not name:
                    name = 'Q%03d' % utility.next_version()
            return normalizer.normalize(name)
        # EvaluationSheet
        elif IEvaluationSheet.providedBy(object):
            normalizer = getUtility(IURLNormalizer)
            if not name:
                # first check if object has an id
                name = getattr(aq_base(object), 'id', None)
                if not name:
                    name = 'evaluationsheet-%s-%s' %\
                           (object.assessment.to_object.id,
                            object.classlist.to_object.id)
                name = self._findUniqueName(name,object)
            return normalizer.normalize(name)
        # All other objects
        else:
            return super(AssessmentItemNameChooser, self).chooseName(
                name, object)

