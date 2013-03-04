import logging
from zope.component import getUtility
from zope.component.hooks import getSite
from plone.app.controlpanel.security import ISecuritySchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.permissions import ModifyViewTemplate
from Products.ATContentTypes.permission import ModifyConstrainTypes
from Products.ATContentTypes.lib.constraintypes import ENABLED

PROFILE_ID = 'profile-tarmii.theme.theme:default'

log = logging.getLogger('tarmii.theme-setuphandlers')

sitefolders = (
    ('topictrees', 'topictrees', 'Topic Trees', 
        ['collective.topictree.topictree']),
    ('activities', 'activities', 'Activities', 
        ['upfront.assessmentitem.content.assessmentitem',
         'upfront.assessmentitem.content.introtext']),
    ('resources', 'resources', 'Teacher Resources',
        ['tarmii.theme.content.teacherresource']),
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

    # allow members to create activities
    portal.activities.manage_setLocalRoles('AuthenticatedUsers',
        ['Contributor', 'Editor', 'Reader'])

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
        langtree.use_with_activities = True
        langtree.use_with_resources = True
        langtree.invokeFactory('collective.topictree.topic',
                               'afrikaans', title='Afrikaans')
        langtree.invokeFactory('collective.topictree.topic',
                               'english', title='English')
        langtree.invokeFactory('collective.topictree.topic',
                               'isindebele', title='Isindebele')
        langtree.invokeFactory('collective.topictree.topic',
                               'isixhosa', title='IsiXhosa')
        langtree.invokeFactory('collective.topictree.topic',
                               'isizulu', title='IsiZulu')
        langtree.invokeFactory('collective.topictree.topic',
                               'sepedi', title='Sepedi')
        langtree.invokeFactory('collective.topictree.topic',
                               'sesotho', title='Sesotho')
        langtree.invokeFactory('collective.topictree.topic',
                               'setswana', title='Setswana')
        langtree.invokeFactory('collective.topictree.topic',
                               'siswati', title='Siswati')
        langtree.invokeFactory('collective.topictree.topic',
                               'tshivenda', title='Tshivenda')
        langtree.invokeFactory('collective.topictree.topic',
                               'xitsonga', title='Xitsonga')

    if not topicfolder.hasObject('grade'):
        topicfolder.invokeFactory('collective.topictree.topictree',
                                  'grade', title='Grade')
        tree = topicfolder._getOb('grade')
        tree.use_with_activities = True
        tree.use_with_resources = True
        for i in range(1,5):
            grade_id = 'grade%s' % i
            grade_title = 'Grade %s' % i
            tree.invokeFactory('collective.topictree.topic',
                               grade_id, title=grade_title)

    if not topicfolder.hasObject('term'):
        topicfolder.invokeFactory('collective.topictree.topictree',
                                  'term', title='Term')
        tree = topicfolder._getOb('term')
        tree.use_with_activities = True
        tree.use_with_resources = False
        for i in range(1,5):
            term_id = 'term%s' % i
            term_title = 'Term %s' % i
            tree.invokeFactory('collective.topictree.topic',
                               term_id, title=term_title)

    if not topicfolder.hasObject('subject'):
        topicfolder.invokeFactory('collective.topictree.topictree',
                                  'subject', title='Subject')
        tree = topicfolder._getOb('subject')
        tree.use_with_activities = True
        tree.use_with_resources = True
        tree.invokeFactory('collective.topictree.topic',
                           'lang', title='Language')
        tree.invokeFactory('collective.topictree.topic',
                           'mathematics', title='Mathematics')
        tree.invokeFactory('collective.topictree.topic',
                           'lifeskills', title='Life Skills')


    # set cookie auth url
    acl = getToolByName(portal, 'acl_users')
    acl.credentials_cookie_auth.login_path = '@@select-profile'

    # set TinyMCE link using UIDs
    ptmce = getToolByName(portal, 'portal_tinymce')
    ptmce.link_using_uids = True

    # language settings
    pl = getToolByName(portal, 'portal_languages')
    # xh - isixhosa
    # st - sesotho
    # ss - siswati
    # ve - tsivenda
    # ts - xisonga
    # tn - setswana
    # zu - isizulu
    # nd - ndebele north
    # nr - isindebele (ndebele south)
    # set allowed languages
    pl.supported_langs = ['af','en','nr','xh','zu','st','tn','ss','ve','ts']

    # Use cookie for manual override. 
    pl.use_cookie_negotiation = True
    # Set the language cookie always
    pl.set_cookie_everywhere = True


def setup(context):
    # Only run step if a flag file is present
    if context.readDataFile('tarmii.theme_marker.txt') is None:
        return
    site = context.getSite()
    setupPortalContent(site)
