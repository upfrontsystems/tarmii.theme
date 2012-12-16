from zope.interface import Interface
from five import grok

grok.templatedir('templates')

class SelectProfileView(grok.View):
    """ View for displaying all non-admin users in the system and allowing users
        to log in with a click.
    """
    grok.context(Interface)
    grok.name('select-profile')
    grok.template('selectprofile')
    grok.require('zope2.View')

    def profiles(self):
        """ Return all non-admin users in the system.
        """
        return ''

