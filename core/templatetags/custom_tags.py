from django import template
from django.forms import FileInput, TextInput, Textarea

register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={'class': css})

@register.filter(name='is_widget_type')
def is_widget_type(field, widget_type):
    widget_classes = {
        'TextInput': TextInput,
        'FileInput': FileInput,
        'Textarea': Textarea
    }
    return isinstance(field.field.widget, widget_classes[widget_type])