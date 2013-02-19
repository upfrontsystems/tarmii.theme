import zope.interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.form import interfaces

from plone.formwidget.contenttree.widget import ContentTreeWidget

from tarmii.theme import MessageFactory as _

class ITopicsWidget(interfaces.IWidget):
    """ Topics Widget
    """


class TopicsWidget(ContentTreeWidget):
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


@zope.interface.implementer(interfaces.IFieldWidget)
def topicsFieldWidgetFactory(field, request):
    """IFieldWidget factory for TopicsWidget."""
    return widget.FieldWidget(field, TopicsWidget(request))


@zope.interface.implementer(interfaces.IFieldWidget)
def TopicsFieldWidget(field, request):
    """IFieldWidget factory for TopicsWidget."""
    return topicsFieldWidgetFactory(field, request)
