import logging

from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.permissions import ModifyViewTemplate
from Products.ATContentTypes.permission import ModifyConstrainTypes
from Products.ATContentTypes.lib.constraintypes import ENABLED

PROFILE_ID = 'profile-tarmii.theme.app:default'

log = logging.getLogger('tarmii.theme-setuphandlers')

sitefolders = (
    ('topics', 'Topics', 
        ['collective.topictree.topictree']),
    ('assessmentitems', 'Assessment Items', 
        ['upfront.assessmentitem.content.assessmentitemcontainer']),
    ('resources', 'Teacher Resources', ['File']),
)

def setupPortalContent(portal):
    # delete all content in the root
    for objId in ('front-page', 'Members', 'news', 'events'):
        if portal.hasObject(objId):
            portal.manage_delObjects(ids=objId)

    for folder_id, title, allowed_types in sitefolders:
        if not portal.hasObject(folder_id):
            portal.invokeFactory(type_name='Folder', id=folder_id, title=title)
        folder = portal._getOb(folder_id)
        folder.setConstrainTypesMode(ENABLED)
        folder.setLocallyAllowedTypes(allowed_types)
        folder.setImmediatelyAddableTypes(allowed_types)

        # Nobody is allowed to modify the constraints or tweak the
        # display here
        folder.manage_permission(ModifyConstrainTypes, roles=[])
        folder.manage_permission(ModifyViewTemplate, roles=[])


def setup(context):
    # Only run step if a flag file is present
    if context.readDataFile('tarmii.theme_marker.txt') is None:
        return
    site = context.getSite()
    setupPortalContent(site)
