import zope.component
from z3c.form import interfaces

# patch for z3c.form.widget.MultiWidget
def getWidget(self, idx):
    """Setup widget based on index id with or without value."""
    valueType = self.field.value_type
    widget = zope.component.getMultiAdapter((valueType, self.request),
        interfaces.IFieldWidget)
    self.setName(widget, idx)
    widget.mode = self.mode
    widget.context = self.context

    #set widget.form (objectwidget needs this)
    if interfaces.IFormAware.providedBy(self):
        widget.form = self.form
        zope.interface.alsoProvides(
            widget, interfaces.IFormAware)
    widget.update()
    return widget

# patch for z3c.form.object.ObjectWidget
def updateWidgets(self, setErrors=True):
    if self._value is not interfaces.NO_VALUE:
        self._getForm(self._value)
    else:
        self._getForm(None)
        self.subform.ignoreContext = True

    self.subform.context = self.context

    self.subform.update()
    if setErrors:
        self.subform._validate()

