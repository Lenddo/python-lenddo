import sys

ver = sys.version_info

is_py2 = (ver[0] == 2)  # python 2.x
is_py3 = (ver[0] == 3)  # python 3.x


if is_py2:
    from urllib import quote
    from urllib2 import HTTPHandler, HTTPSHandler, Request, build_opener, \
        ProxyHandler
elif is_py3:
    from urllib.parse import quote
    from urllib.request import HTTPHandler, HTTPSHandler, Request, \
        build_opener, ProxyHandler
