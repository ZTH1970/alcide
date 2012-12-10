from django import template

register = template.Library()

@register.filter
def is_worker_in_service(worker, service_name):
    for service in worker.services.all():
        if service.name == service_name:
            return True
    return False
