import zope.interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component.hooks import getSite
from z3c.form import interfaces
from z3c.form import widget
from plone.formwidget.contenttree.widget import MultiContentTreeWidget
from Products.CMFCore.utils import getToolByName
from tarmii.theme import MessageFactory as _

class ITopicsWidget(interfaces.IWidget):
    """ Topics Widget
    """


class TopicsWidget(MultiContentTreeWidget):
    """ Extend content tree widget """

    zope.interface.implements(ITopicsWidget)

    input_template = ViewPageTemplateFile(
        "templates/topicswidget_input.pt")

    display_template = ViewPageTemplateFile(
        "templates/topicswidget_display.pt")

    def render(self):
        if self.mode == interfaces.INPUT_MODE:
            return self.input_template(self)
        else:
            return MultiContentTreeWidget.render(self)

    def topictrees(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        # if we are in the activities folder - check activities filter
        if self.context.id == 'activities':
            for x in brains:
                if x.getObject().use_with_activities:
                    topictree_list.append(x)
            return topictree_list
        # if we are in the activities folder - check activities filter
        if self.context.id == 'resources':
            for x in brains:
                if x.getObject().use_with_resources:
                    topictree_list.append(x)
            return topictree_list

        # if we are not in the activities or resources folder, display all 
        # topictrees in the system
        return brains

    def topic_selected(self, topic):
        return topic.getPath() in self.value


@zope.interface.implementer(interfaces.IFieldWidget)
def topicsFieldWidgetFactory(field, request):
    """IFieldWidget factory for TopicsWidget."""
    return widget.FieldWidget(field, TopicsWidget(request))


@zope.interface.implementer(interfaces.IFieldWidget)
def TopicsFieldWidget(field, request):
    """IFieldWidget factory for TopicsWidget."""
    return topicsFieldWidgetFactory(field, request)
