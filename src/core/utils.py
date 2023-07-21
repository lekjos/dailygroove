from typing import List

from django.utils.http import urlencode


def replace_url_params(request, skip_encode_params: List[str] = [], **kwargs):
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
                else:
                    return urlencode({k: v})

            params = "&".join([_encode(k, v) for k, v in params.items()])
            return f"?{params}"
        return f"?{params.urlencode()}"
    return ""
