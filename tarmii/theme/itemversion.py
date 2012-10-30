from zope.component import queryUtility
from five import grok
from plone.registry.interfaces import IRegistry

from tarmii.theme.interfaces import IItemVersion
from tarmii.theme.interfaces import ILastItemVersionNumber

class ItemVersion(grok.GlobalUtility):
    """ Very simple utility that 
    """
    grok.provides(IItemVersion)

    def next_version(self):
        registry = queryUtility(IRegistry)
        record = registry.forInterface(ILastItemVersionNumber)
        record.version += 1
        return record.version
