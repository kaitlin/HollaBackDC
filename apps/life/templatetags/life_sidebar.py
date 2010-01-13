from django.template import Library
from life.models import LifeFlow, LifeEvent

register = Library()

@register.inclusion_tag('life/sidebar_flows.html', takes_context=True)
def life_sidebar_flows(context):
    return {
            'lifeflows': LifeFlow.objects.active(),
            }

@register.inclusion_tag('life/sidebar_events.html', takes_context=True)
def life_sidebar_events(context):
    return {
            'lifeevents': LifeEvent.objects.active().order_by('-posted')[:5],
            }

