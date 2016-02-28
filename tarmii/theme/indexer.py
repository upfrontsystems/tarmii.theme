from upfront.assessmentitem.content.assessmentitem import IAssessmentItem
from plone.indexer.decorator import indexer
from plone.uuid.interfaces import IUUID

@indexer(IAssessmentItem)
def topic_uids(obj, **kw):
     return [IUUID(rel.to_object) for rel in obj.topics]
