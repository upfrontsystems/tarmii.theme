import zope.interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component.hooks import getSite
from z3c.form import interfaces
from z3c.form import widget

from plone.formwidget.contenttree.widget import MultiContentTreeWidget

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
            return ContentTreeWidget.render(self)

    def topictrees(self):
        """ return the contents of the topictrees folder.
        """
        return getSite().topictrees.getFolderContents()


@zope.interface.implementer(interfaces.IFieldWidget)
def topicsFieldWidgetFactory(field, request):
    """IFieldWidget factory for TopicsWidget."""
    return widget.FieldWidget(field, TopicsWidget(request))


@zope.interface.implementer(interfaces.IFieldWidget)
def TopicsFieldWidget(field, request):
    """IFieldWidget factory for TopicsWidget."""
    return topicsFieldWidgetFactory(field, request)
