import urllib.parse

from django import template

from core.middleware.invite_token_middleware import replace_url_params

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    return replace_url_params(context["request"], **kwargs)


def get_youtube_embed(url):
    # Check if the link is from youtube.com or youtu.be
    YT_DOMAINS = ["youtube.com", "youtu.be"]
    is_youtube = any(x in url for x in YT_DOMAINS)
    if not is_youtube:
        return False

    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    if "youtube.com/watch" in url and "v=" in url:
        video_id = query_params.get("v")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1][:11]

    embed_link = f"https://www.youtube.com/embed/{video_id}"
    if timestamp := query_params.get("t", ""):
        embed_link += f"?start={timestamp}"

    return embed_link


@register.filter(name="youtube_embed_url")
# converts youtube URL into embed HTML
# value is url
def youtube_embed_url(url, title=""):
    embed_url = get_youtube_embed(url)
    if embed_url:
        res = f'<iframe width="560" height="315" src="{embed_url}" title="{title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
        return res

    return ""


youtube_embed_url.is_safe = True
