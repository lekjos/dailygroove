from django.conf import settings


def global_processor(request):
    """
    Adds globally available context for base template.
    """
    root_url = settings.ROOT_URL

    return {
        "root_url": root_url,
    }
