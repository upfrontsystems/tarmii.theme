import logging

from plone.app.controlpanel.security import ISecuritySchema
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.permissions import ModifyViewTemplate
from Products.ATContentTypes.permission import ModifyConstrainTypes
from Products.ATContentTypes.lib.constraintypes import ENABLED

from Products.CMFCore.WorkflowCore import WorkflowException

PROFILE_ID = 'profile-tarmii.theme.theme:default'

log = logging.getLogger('tarmii.theme-setuphandlers')

sitefolders = (
    ('topictrees', 'topictrees', 'Topic Trees', 
        ['collective.topictree.topictree']),
    ('activities', 'activities', 'Activities', 
        ['upfront.assessmentitem.content.assessmentitem',
         'upfront.assessmentitem.content.introtext']),
    ('resources', 'resources', 'Teacher Resources', ['File']),
    ('videos', 'videos', 'Videos', ['File','Image']),
)

def setupPortalContent(portal):
    # delete all content in the root
    for objId in ('front-page', 'news', 'events'):
        if portal.hasObject(objId):
            portal.manage_delObjects(ids=objId)

    # disable tabs
    pprop = getToolByName(portal, 'portal_properties')
    pprop.site_properties._updateProperty('disable_folder_sections', True)

    pw = getToolByName(portal, 'portal_workflow')

    for folder_id, layout, title, allowed_types in sitefolders:
        if not portal.hasObject(folder_id):
            portal.invokeFactory(type_name='Folder', id=folder_id, title=title)
        folder = portal._getOb(folder_id)
        if layout:
            folder.setLayout(layout)
        folder.setConstrainTypesMode(ENABLED)
        folder.setLocallyAllowedTypes(allowed_types)
        folder.setImmediatelyAddableTypes(allowed_types)

        # Nobody is allowed to modify the constraints or tweak the
        # display here
        folder.manage_permission(ModifyConstrainTypes, roles=[])
        folder.manage_permission(ModifyViewTemplate, roles=[])

        # transition top level folder to the "internally published" state.
        state = pw.getStatusOf('intranet_workflow',folder)['review_state']
        if state == 'private':
            try:
                pw.doActionFor(folder, "show_internally")
            except WorkflowException:
                pass
        if state == 'internal' or state == 'pending':
            try:
                pw.doActionFor(folder, "publish_internally")
            except WorkflowException:
                pass

    # allow member folders to be created
    security_adapter =  ISecuritySchema(portal)
    security_adapter.set_enable_user_folders(True)
    # enable self-registration of users
    security_adapter.set_enable_self_reg(True)

    # create basic language topictree
    topicfolder = portal._getOb('topictrees')
    if not topicfolder.hasObject('language'):
        topicfolder.invokeFactory('collective.topictree.topictree',
                                  'language', title='Language')
        langtree = topicfolder._getOb('language')
        langtree.invokeFactory('collective.topictree.topic',
                                'afrikaans', title='Afrikaans')
        langtree.invokeFactory('collective.topictree.topic',
                                'english', title='English')
        langtree.invokeFactory('collective.topictree.topic',
                                'xhosa', title='Xhosa')

    # set cookie auth url
    acl = getToolByName(portal, 'acl_users')
    acl.credentials_cookie_auth.login_path = '@@select-profile'


def setup(context):
    # Only run step if a flag file is present
    if context.readDataFile('tarmii.theme_marker.txt') is None:
        return
    site = context.getSite()
    setupPortalContent(site)
