import logging

from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.permissions import ModifyViewTemplate
from Products.ATContentTypes.permission import ModifyConstrainTypes
from Products.ATContentTypes.lib.constraintypes import ENABLED

PROFILE_ID = 'profile-tarmii.theme.app:default'

log = logging.getLogger('tarmii.theme-setuphandlers')

def setupPortalContent(portal):

    # setup Resources folder
    if not portal.hasObject('resources'):
        portal.invokeFactory(type_name='Folder', id='resources',
                             title='Resources')
    folder = portal._getOb('resources')
    folder.setLayout('resources')
    folder.setConstrainTypesMode(ENABLED)
    folder.setLocallyAllowedTypes(['collective.topictree.topictree',
                                   'collective.topictree.topic'])
    folder.setImmediatelyAddableTypes(['collective.topictree.topictree',
                                       'collective.topictree.topic'])
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
