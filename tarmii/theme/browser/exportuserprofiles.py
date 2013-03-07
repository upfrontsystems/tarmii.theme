from csv import DictWriter
from cStringIO import StringIO
from DateTime import DateTime

from five import grok
from zope.interface import Interface

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import getToolByName

from tarmii.theme import MessageFactory as _

class ExportUserProfilesView(grok.View):
    """ Export all user profiles with columns for all fields captured during 
        registration as well as the first time the user logged as well as the
        last login time.
    """
    grok.context(Interface)
    grok.name('export-user-profiles')
    grok.require('cmf.ManagePortal')

    def user_profiles_csv(self):
        """ Export all user profiles with columns for all fields captured during 
            registration as well as the first time the user logged as well as 
            the last login time.
        """

        csv_content = None
        profiles_csv = StringIO()

        pm = getToolByName(self.context, 'portal_membership')
        # get all user profiles in the system
        user_profiles = pm.listMembers()

        if user_profiles is not None and len(user_profiles) > 0:
            writer = DictWriter(profiles_csv,
                                fieldnames=['username', 'fullname', 'email',
                                            'teacher_mobile_number', 'school',
                                            'province', 'EMIS',
                                            'school_contact_number',
                                            'school_email', 'qualification',
                                            'years_teaching','last_login_time',
                                            'uuid'],
                                restval='',
                                extrasaction='ignore',
                                dialect='excel'
                               )

            for user in user_profiles:
                ldict={'username': user.id,
                       'fullname': user.getProperty('fullname'),
                       'email': user.getProperty('email'),
                       'teacher_mobile_number': user.getProperty('teacher_mobile_number'),
                       'school': user.getProperty('school'),
                       'province': user.getProperty('province'),
                       'EMIS': user.getProperty('EMIS'),
                       'school_contact_number': 
                                    user.getProperty('school_contact_number'),
                       'school_email': user.getProperty('school_email'),
                       'qualification': user.getProperty('qualification'),
                       'years_teaching': user.getProperty('years_teaching'),
                       'last_login_time': 
                   user.getProperty('login_time').strftime('%d/%m/%Y %H:%M:%S'),
                       'uuid': user.getProperty('uuid'),
                        # 'login_time' is really the latest login
                        # 'last_login_time' is the time user was logged in the
                        # time before 'login_time'
                      }
                writer.writerow(ldict)
           
            csv_content = profiles_csv.getvalue()
            profiles_csv.close()

        return csv_content

    def __call__(self):
        """ Return csv content as http response or return info IStatusMessage
        """

        csv_content = self.user_profiles_csv()

        if csv_content is not None:
            now = DateTime()
            nice_filename = '%s_%s' % ('userprofiles_', now.strftime('%Y%m%d'))

            self.request.response.setHeader("Content-Disposition",
                                            "attachment; filename=%s.csv" % 
                                             nice_filename)
            self.request.response.setHeader("Content-Type", "text/csv")
            self.request.response.setHeader("Content-Length", len(csv_content))
            self.request.response.setHeader('Last-Modified',
                                            DateTime.rfc822(DateTime()))
            self.request.response.setHeader("Cache-Control", "no-store")
            self.request.response.setHeader("Pragma", "no-cache")
            self.request.response.write(csv_content)
        else:
            msg = _('No user profiles exist')
            IStatusMessage(self.request).addStatusMessage(msg,"info")

        # redirect to show the info message
        self.request.response.redirect(
                '/'.join(self.context.getPhysicalPath()))

        return csv_content

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''
