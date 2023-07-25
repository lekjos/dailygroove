from typing import List, Optional

from django.contrib import admin
from django.utils.http import urlencode


def replace_url_params(
    request, skip_encode_params: Optional[List[str]] = None, **kwargs
):
    """
    replaces kwargs in a url
    """
    params = request.GET.copy()
    for k, v in kwargs.items():
        params[k] = v

    empty_param_keys = [k for k, v in params.items() if not v]
    for k in empty_param_keys:
        del params[k]
    if params:
        if skip_encode_params:

            def _encode(k, v) -> str:
                if k in skip_encode_params:
                    return f"{k}={v}"
                return urlencode({k: v})

            params = "&".join([_encode(k, v) for k, v in params.items()])
            return f"?{params}"
        return f"?{params.urlencode()}"
    return ""


class IsNullFilter(admin.SimpleListFilter):
    """Admin Filter for determining if fk is null
    - title: Title in admin
    - parameter_name: url param string
    - field_lookup: field_name string to check {field_name}__isnull

    """

    title = "TITLE IN ADMIN"
    parameter_name = "url_param_name"
    field_lookup = "name_of_alias"

    def lookups(self, request, model_admin):
        return (
            ("true", "True"),
            ("false", "False"),
        )

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(**{f"{self.field_lookup}__isnull": True}).distinct()
        if self.value() == "false":
            return queryset.filter(**{f"{self.field_lookup}__isnull": False}).distinct()
        return queryset
