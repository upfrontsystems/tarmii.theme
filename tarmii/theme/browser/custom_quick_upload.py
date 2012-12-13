# code taken from collective.uploadify
# for the flashupload
# with many ameliorations

import os
import mimetypes
import random
import urllib

from Acquisition import aq_inner, aq_parent
from AccessControl import SecurityManagement
from ZPublisher.HTTPRequest import HTTPRequest
from zope.security.interfaces import Unauthorized
from zope.component import getUtility
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interfaces import IImageContent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Sessions.SessionDataManager import SessionDataManagerErr
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer


import pkg_resources
try:
    pkg_resources.get_distribution('plone.uuid')
    from plone.uuid.interfaces import IUUID
    HAS_UUID = True
except pkg_resources.DistributionNotFound:
    HAS_UUID = False

import collective.quickupload.browser.ticket as ticketmod
from collective.quickupload import siteMessageFactory as _
from collective.quickupload import logger
from collective.quickupload.browser.quickupload_settings import IQuickUploadControlPanel
from collective.quickupload.interfaces import (
    IQuickUploadNotCapable, IQuickUploadFileFactory, IQuickUploadFileUpdater)

from collective.quickupload.browser.uploadcapable import get_id_from_filename,\
    MissingExtension

from collective.quickupload.browser.quick_upload import QuickUploadView,\
    QuickUploadInit
    
try :
    # python 2.6
    import json
except ImportError:
    # plone 3.3
    import simplejson as json

class CustomQuickUploadView(QuickUploadView):
    """ Custom Quick Upload View
    """

    template = ViewPageTemplateFile("templates/quick_upload.pt")

    def __init__(self, context, request):
        super(QuickUploadView, self).__init__(context, request)
        self.uploader_id = self._uploader_id()

    def __call__(self):
        if IQuickUploadNotCapable.providedBy(self.context):
            raise Unauthorized

#        # disable diazo themes
#        self.request.response.setHeader('X-Theme-Disabled', 'False')

        return self.template()

    def header_upload(self) :
        request = self.request
        try:
            session = request.get('SESSION', {})
            medialabel = session.get('mediaupload',
                    request.get('mediaupload', 'files'))
        except SessionDataManagerErr:
            logger.debug('Error occurred getting session data. '
                         'Falling back to request.')
            medialabel = request.get('mediaupload', 'files')

        # to improve
        if '*.' in medialabel :
            medialabel = ''
        if not medialabel :
            return _('Files Quick Upload')
        elif medialabel == 'image' :
            return _('Images Quick Upload')
        else:
            return _('label_media_quickupload',
                     default='${medialabel} Quick Upload',
                     mapping={'medialabel': medialabel.capitalize()})

    def _uploader_id(self) :
        return 'uploader%s' %str(random.random()).replace('.','')

    def script_content(self) :
        context = aq_inner(self.context)
        return context.restrictedTraverse('@@quick_upload_init')(for_id = self.uploader_id)

    def can_drag_and_drop(self):

       user_agent = self.request.get_header('User-Agent')
       if user_agent and (("msie" in user_agent.lower())
           or ("microsoft internet explorer" in user_agent.lower())):
           return False
       else:
           return True


XHR_UPLOAD_JS = """
    var fillTitles = %(ul_fill_titles)s;
    var fillDescriptions = %(ul_fill_descriptions)s;
    var auto = %(ul_auto_upload)s;
    var Browser = {};
    Browser.onUploadComplete = function() {
        window.location.reload();
    }
    addUploadFields_%(ul_id)s = function(file, id) {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.addUploadFields(uploader, uploader._element, file, id, fillTitles, fillDescriptions);
    }
    sendDataAndUpload_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.sendDataAndUpload(uploader, uploader._element, '%(typeupload)s');
    }
    clearQueue_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.clearQueue(uploader, uploader._element);
    }
    onUploadComplete_%(ul_id)s = function(id, fileName, responseJSON) {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.onUploadComplete(uploader, uploader._element, id, fileName, responseJSON);
    }
    createUploader_%(ul_id)s= function(){
        xhr_%(ul_id)s = new qq.FileUploader({
            element: jQuery('#%(ul_id)s')[0],
            action: '%(context_url)s/@@quick_upload_file',
            autoUpload: auto,
            onAfterSelect: addUploadFields_%(ul_id)s,
            onComplete: onUploadComplete_%(ul_id)s,
            allowedExtensions: %(ul_file_extensions_list)s,
            sizeLimit: %(ul_xhr_size_limit)s,
            simUploadLimit: %(ul_sim_upload_limit)s,
            template: '<div class="qq-uploader">' +
                      '<div class="qq-upload-drop-area"><span>%(ul_draganddrop_text)s</span></div>' +
                      '<div class="qq-upload-button">%(ul_button_text)s</div>' +
                      '<ul class="qq-upload-list"></ul>' +
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(ul_msg_failed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',
            messages: {
                serverError: "%(ul_error_server)s",
                serverErrorAlreadyExists: "%(ul_error_already_exists)s {file}",
                serverErrorZODBConflict: "%(ul_error_zodb_conflict)s {file}, %(ul_error_try_again)s",
                serverErrorNoPermission: "%(ul_error_no_permission)s",
                serverErrorDisallowedType: "%(ul_error_disallowed_type)s",
                typeError: "%(ul_error_bad_ext)s {file}. %(ul_error_onlyallowed)s {extensions}.",
                sizeError: "%(ul_error_file_large)s {file}, %(ul_error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(ul_error_empty_file)s {file}, %(ul_error_try_again_wo)s",
                missingExtension: "%(ul_error_empty_extension)s {file}"
            }
        });
    }
    jQuery(document).ready(createUploader_%(ul_id)s);
"""

FLASH_UPLOAD_JS = """
    var fillTitles = %(ul_fill_titles)s;
    var fillDescriptions = %(ul_fill_descriptions)s;
    var autoUpload = %(ul_auto_upload)s;
    clearQueue_%(ul_id)s = function() {
        jQuery('#%(ul_id)s').uploadifyClearQueue();
    }
    addUploadifyFields_%(ul_id)s = function(event, data ) {
        if ((fillTitles || fillDescriptions) && !autoUpload)  {
            var labelfiletitle = jQuery('#uploadify_label_file_title').val();
            var labelfiledescription = jQuery('#uploadify_label_file_description').val();
            jQuery('#%(ul_id)sQueue .uploadifyQueueItem').each(function() {
                ID = jQuery(this).attr('id').replace('%(ul_id)s','');
                if (!jQuery('.uploadField' ,this).length) {
                  jQuery('.cancel' ,this).after('\
                          <input type="hidden" \
                                 class="file_id_field" \
                                 name="file_id" \
                                 value ="'  + ID + '" /> \
                  ');
                  if (fillDescriptions) jQuery('.cancel' ,this).after('\
                      <div class="uploadField">\
                          <label>' + labelfiledescription + ' : </label> \
                          <textarea rows="2" \
                                 class="file_description_field" \
                                 id="description_' + ID + '" \
                                 name="description" \
                                 value="" />\
                      </div>\
                  ');
                  if (fillTitles) jQuery('.cancel' ,this).after('\
                      <div class="uploadField">\
                          <label>' + labelfiletitle + ' : </label> \
                          <input type="text" \
                                 class="file_title_field" \
                                 id="title_' + ID + '" \
                                 name="title" \
                                 value="" />\
                      </div>\
                  ');
                }
            });
        }
        if (!autoUpload) return showButtons_%(ul_id)s();
        return 'ok';
    }
    showButtons_%(ul_id)s = function() {
        if (jQuery('#%(ul_id)sQueue .uploadifyQueueItem').length) {
            jQuery('.uploadifybuttons').show();
            return 'ok';
        }
        return false;
    }
    sendDataAndUpload_%(ul_id)s = function() {
        QueueItems = jQuery('#%(ul_id)sQueue .uploadifyQueueItem');
        nbItems = QueueItems.length;
        QueueItems.each(function(i){
            filesData = {};
            ID = jQuery('.file_id_field',this).val();
            if (fillTitles && !autoUpload) {
                filesData['title'] = jQuery('.file_title_field',this).val();
            }
            if (fillDescriptions && !autoUpload) {
                filesData['description'] = jQuery('.file_description_field',this).val();
            }
            jQuery('#%(ul_id)s').uploadifySettings('scriptData', filesData);
            jQuery('#%(ul_id)s').uploadifyUpload(ID);
        })
    }
    onAllUploadsComplete_%(ul_id)s = function(event, data){
        if (!data.errors) {
           Browser.onUploadComplete();
        }
        else {
           msg= data.filesUploaded + '%(ul_msg_some_sucess)s' + data.errors + '%(ul_msg_some_errors)s';
           alert(msg);
        }
    }
    jQuery(document).ready(function() {
        jQuery('#%(ul_id)s').uploadify({
            'uploader'      : '%(portal_url)s/++resource++quickupload_static/uploader.swf',
            'script'        : '%(context_url)s/@@flash_upload_file',
            'cancelImg'     : '%(portal_url)s/++resource++quickupload_static/cancel.png',
            'folder'        : '%(physical_path)s',
            'onAllComplete' : onAllUploadsComplete_%(ul_id)s,
            'auto'          : autoUpload,
            'multi'         : true,
            'simUploadLimit': %(ul_sim_upload_limit)s,
            'sizeLimit'     : '%(ul_size_limit)s',
            'fileDesc'      : '%(ul_file_description)s',
            'fileExt'       : '%(ul_file_extensions)s',
            'buttonText'    : '%(ul_button_text)s',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false,
            'onSelectOnce'  : addUploadifyFields_%(ul_id)s,
            'scriptData'    : {'ticket' : '%(ticket)s', 'typeupload' : '%(typeupload)s'}
        });
    });
"""


class CustomQuickUploadInit(QuickUploadInit):
    """ Custom Initialize uploadify js
    """

    def __init__(self, context, request):
        super(QuickUploadInit, self).__init__(context, request)
        self.context = aq_inner(context)
        portal = getUtility(IPloneSiteRoot)
        self.qup_prefs = IQuickUploadControlPanel(portal)

    def ul_content_types_infos (self, mediaupload):
        """
        return some content types infos depending on mediaupload type
        mediaupload could be 'image', 'video', 'audio' or any
        extension like '*.doc'
        """
        ext = '*.*;'
        extlist = []
        msg = u'Choose files to upload'
        if mediaupload == 'image' :
            ext = '*.jpg;*.jpeg;*.gif;*.png;'
            msg = _(u'Choose images to upload')
        elif mediaupload == 'video' :
            ext = '*.flv;*.avi;*.wmv;*.mpg;'
            msg = _(u'Choose video files to upload')
        elif mediaupload == 'audio' :
            ext = '*.mp3;*.wav;*.ogg;*.mp4;*.wma;*.aif;'
            msg = _(u'Choose audio files to upload')
        elif mediaupload == 'flash' :
            ext = '*.swf;'
            msg = _(u'Choose flash files to upload')
#        elif mediaupload :
#            # you can also pass a list of extensions in mediaupload request var
#            # with this syntax '*.aaa;*.bbb;'
#            ext = mediaupload
#            msg = _(u'Choose file for upload: ${ext}', mapping={'ext': ext})
        elif mediaupload == '':
            # the original code was setup to use the mediaload but we set our 
            # restrictions instead when the mediaupload parameter is not in use
            # at all.
            ext = '*.flv;*.mp4;'
            msg = _(u'Choose file for upload: ${ext}', mapping={'ext': ext})


        try :
            extlist = [f.split('.')[1].strip() for f in ext.split(';') if f.strip()]
        except :
            extlist = []
        if extlist==['*'] :
            extlist = []

        return ( ext, extlist, self._translate(msg))

    def _translate(self, msg):
        return translate(msg, context=self.request)

    def upload_settings(self):
        context = aq_inner(self.context)
        request = self.request
        try:
            session = request.get('SESSION', {})
            mediaupload = session.get('mediaupload',
                    request.get('mediaupload', ''))
            typeupload = session.get('typeupload',
                    request.get('typeupload', ''))
        except SessionDataManagerErr:
            logger.debug('Error occurred getting session data. Falling back to '
                    'request.')
            mediaupload = request.get('mediaupload', '')
            typeupload = request.get('typeupload', '')
        portal_url = getToolByName(context, 'portal_url')()
        # use a ticket for authentication (used for flashupload only)
        ticket = context.restrictedTraverse('@@quickupload_ticket')()

        settings = dict(
            ticket                 = ticket,
            portal_url             = portal_url,
            typeupload             = '',
            context_url            = context.absolute_url(),
            physical_path          = "/".join(context.getPhysicalPath()),
            ul_id                  = self.uploader_id,
            ul_fill_titles         = self.qup_prefs.fill_titles and 'true' or 'false',
            ul_fill_descriptions   = self.qup_prefs.fill_descriptions and 'true' or 'false',
            ul_auto_upload         = self.qup_prefs.auto_upload and 'true' or 'false',
            ul_size_limit          = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '',
            ul_xhr_size_limit      = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '0',
            ul_sim_upload_limit    = str(self.qup_prefs.sim_upload_limit),
            ul_button_text         = self._translate(_(u'Add video ')),
            ul_draganddrop_text    = self._translate(_(u'Drag and drop files to upload')),
            ul_msg_all_sucess      = self._translate(_(u'All files uploaded with success.')),
            ul_msg_some_sucess     = self._translate(_(u' files uploaded with success, ')),
            ul_msg_some_errors     = self._translate(_(u" uploads return an error.")),
            ul_msg_failed          = self._translate(_(u"Failed")),
            ul_error_try_again_wo  = self._translate(_(u"please select files again without it.")),
            ul_error_try_again     = self._translate(_(u"please try again.")),
            ul_error_empty_file    = self._translate(_(u"Selected elements contain an empty file or a folder:")),
            ul_error_empty_extension = self._translate(_(u"This file has no extension:")),
            ul_error_file_large    = self._translate(_(u"This file is too large:")),
            ul_error_maxsize_is    = self._translate(_(u"maximum file size is:")),
            ul_error_bad_ext       = self._translate(_(u"This file has invalid extension:")),
            ul_error_onlyallowed   = self._translate(_(u"Only allowed:")),
            ul_error_no_permission = self._translate(_(u"You don't have permission to add this content in this place.")),
            ul_error_disallowed_type = self._translate(_(u"This type of element is not allowed in this folder.",)),
            ul_error_already_exists = self._translate(_(u"This file already exists with the same name on server:")),
            ul_error_zodb_conflict = self._translate(_(u"A data base conflict error happened when uploading this file:")),
            ul_error_server        = self._translate(_(u"Server error, please contact support and/or try again.")),
        )

        settings['typeupload'] = typeupload
        if typeupload :
            imageTypes = _listTypesForInterface(context, IImageContent)
            if typeupload in imageTypes :
                ul_content_types_infos = self.ul_content_types_infos('image')
            else :
                ul_content_types_infos = self.ul_content_types_infos(mediaupload)
        else :
            ul_content_types_infos = self.ul_content_types_infos(mediaupload)

        settings['ul_file_extensions'] = ul_content_types_infos[0]
        settings['ul_file_extensions_list'] = str(ul_content_types_infos[1])
        settings['ul_file_description'] = ul_content_types_infos[2]

        return settings

    def __call__(self, for_id="uploader"):
        self.uploader_id = for_id
        settings = self.upload_settings()
        if self.qup_prefs.use_flashupload :
            return FLASH_UPLOAD_JS % settings
        return XHR_UPLOAD_JS % settings
