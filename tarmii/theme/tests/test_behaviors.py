"""
Test functionality specific to tarmii.theme and provided by our custom
behaviors.
"""

import transaction
from zope.component import getUtility

from plone.dexterity.utils import createContentInContainer
from tarmii.theme.tests.base import TarmiiThemeTestBase
from tarmii.theme.behaviors import IItemMetadata
from zExceptions import BadRequest


class TestBehaviorValidators(TarmiiThemeTestBase):
    """ 
    """
    
    def test_RatingValidator(self):
        self.fail()

    def test_ItemIdValidator(self):
        raised = False
        item_id = 'a_item_001'
        pc = self.portal.portal_catalog
        query = {
            "portal_type" : "upfront.assessmentitem.content.assessmentitem",
            "item_id": item_id,
        }
        container = self.portal.activities
        settings = {'id'      : 'a_item_001',
                    'item_id' : item_id,}

        a_item = createContentInContainer(
            container,
            portal_type = 'upfront.assessmentitem.content.assessmentitem',
            **settings
        )
        transaction.commit()

        self.assertEqual(a_item.item_id, item_id)
        brains = pc(query)
        self.assertEqual(len(brains), 1, 'There can be only one!')
        
        try:
            a_item = createContentInContainer(
                container,
                portal_type = 'upfront.assessmentitem.content.assessmentitem',
                **settings
            )
        except BadRequest:
            raised = True
        self.assertEqual(raised, True, 'No exception raised!') 
        
        transaction.commit()
        brains = pc(query)
        self.assertEqual(len(brains), 1, 'There can be only one!')
