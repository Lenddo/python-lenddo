from lenddo_api_client.compat import is_py2, is_py3


if is_py2:
    from urllib2 import HTTPError, URLError
elif is_py3:
    from urllib.error import HTTPError, URLError
