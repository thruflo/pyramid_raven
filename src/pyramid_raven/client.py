# -*- coding: utf-8 -*-

"""Provides a GeoIPLookup utility."""

__all__ = [
    'get_raven_client'
]

import logging
logger = logging.getLogger(__name__)

import pprint
import raven

from pyramid.settings import asbool

from .constants import ATTR_METHODS
from .constants import ATTR_PROPERTIES
from .constants import DEFAULT_CLIENT_KWARGS

def as_context_data(request, method_names=None, property_names=None, safe=None):
    """Unpack the data from the request safely into a dictionary.
      
          >>> from mock import Mock
          >>> mock_registry = Mock()
          >>> mock_registry.settings = {}
          >>> from pyramid.request import Request
          >>> r = Request.blank('/')
          >>> r.adhoc_method = lambda *args: 'foo'
          >>> r.adhoc_prop = 'bar'
          >>> r.charset = 'UTF-8'
          >>> r.cookies = {'a': 'b'}
          >>> r.registry=mock_registry
          >>> as_context_data(r)
          {'attributes': {'matchdict': None, 'matched_route': None}, 'cookies': {u'a': u'b'}, 'params (POST)': {}, 'query (GET)': {}, 'headers': {'Host': 'localhost:80'}}
      
      Adds attributes specified in the settings::
      
          >>> mock_registry.settings = {
          ...     'pyramid_raven.additional_request_methods': 'adhoc_method',
          ...     'pyramid_raven.additional_request_properties': 'charset adhoc_prop'
          ... }
          >>> r.registry=mock_registry
          >>> attrs = as_context_data(r)['attributes']
          >>> attrs['adhoc_method'], attrs['adhoc_prop'], attrs['charset']
          ('foo', 'bar', 'UTF-8')
      
    """
    
    # Compose.
    if method_names is None:
        method_names = ATTR_METHODS[:]
    if property_names is None:
        property_names = ATTR_PROPERTIES[:]
    if safe is None:
        safe = pprint.saferepr
    
    # Unpack / prepare.
    settings = request.registry.settings
    strip = lambda s: s.strip()
    
    # Add any additional methods and properties to the
    add_methods = settings.get('pyramid_raven.additional_request_methods')
    add_properties = settings.get('pyramid_raven.additional_request_properties')
    if add_methods:
        additional_names = map(strip, add_methods.split(' '))
        method_names += additional_names
    if add_properties:
        additional_properties = map(strip, add_properties.split(' '))
        property_names += additional_properties
    
    # Get selected request attributes.
    attributes = []
    names = list(set(method_names + property_names))
    for item in sorted(names):
        if not hasattr(request, item):
            continue
        attr = getattr(request, item)
        value = attr if item in property_names else attr()
        attribute = (item, value)
        attributes.append(attribute)
    
    # Get the cookies as a list.
    cookies = request.cookies
    cookie_list = [(k, cookies.get(k)) for k in cookies]
    
    # Get the headers as a list.
    header_list = []
    for k, v in sorted(request.headers.items()):
        if k == u'Cookie':
            continue
        header_list.append((k, v))
    
    # Get the params as a list.
    GET = request.GET
    POST = request.POST
    get_list = [(k, GET.getall(k)) for k in GET]
    post_list = [(k, [safe(v) for v in POST.getall(k)]) for k in POST]
    
    # Return as dict.
    return {
        'attributes': dict(attributes),
        'cookies': dict(cookie_list),
        'headers': dict(header_list),
        'params (POST)': dict(post_list),
        'query (GET)': dict(get_list),
    }

def get_raven_client(request, as_data=None, defaults=None, client_cls=None):
    """Return a configured raven client.
      
          >>> from mock import Mock
          >>> mock_as_data = Mock()
          >>> mock_client_cls = Mock()
          >>> mock_registry = Mock()
          >>> mock_registry.settings = {'raven.foo': 'bar'}
          >>> from pyramid.request import Request
          >>> r = Request.blank('/')
          >>> r.registry = mock_registry
          >>> client = get_raven_client(r, as_data=mock_as_data,
          ...         client_cls=mock_client_cls)
          >>> assert client is mock_client_cls.return_value
          >>> mock_client_cls.assert_called_with(foo='bar',
          ...         context=mock_as_data.return_value, **DEFAULT_CLIENT_KWARGS)
      
      If not ``pyramid_raven.include_request_data`` then we don't parse the request
      for data::
          
          >>> mock_as_data = Mock()
          >>> mock_registry.settings = {'pyramid_raven.include_request_data': False}
          >>> client = get_raven_client(r, as_data=mock_as_data,
          ...         client_cls=mock_client_cls)
          >>> mock_as_data.called
          False
      
      Doesn't fall over if the request parsing errors::
      
          >>> mock_registry.settings = {}
          >>> def mock_as_data(*args):
          ...     raise Exception
          >>> client = get_raven_client(r, as_data=mock_as_data,
          ...         client_cls=mock_client_cls)
      
      Unless told to::
      
          >>> mock_registry.settings = {'pyramid_raven.swallow_parse_errors': False}
          >>> def mock_as_data(*args):
          ...     raise Exception
          >>> get_raven_client(r, as_data=mock_as_data)
          Traceback (most recent call last):
          ...
          Exception
      
    """
    
    # Compose.
    if as_data is None:#pragma: no cover
        as_data = as_context_data
    if defaults is None:#pragma: no cover
        defaults = DEFAULT_CLIENT_KWARGS
    if client_cls is None:#pragma: no cover
        client_cls = raven.Client
    
    # Unpack.
    settings = request.registry.settings
    include_data = settings.get('pyramid_raven.include_request_data', True)
    swallow_errors = settings.get('pyramid_raven.swallow_parse_errors', True)
    should_include_data = asbool(include_data)
    should_swallow_parse_errors = asbool(swallow_errors)
    if not should_include_data:
        context_data = None
    else:
        try:
            context_data = as_data(request)
        except Exception as err:
            if not should_swallow_parse_errors:
                raise
            logger.warn(err, exc_info=True)
            context_data = {u'err': u'Failed to get context data from request'}
    
    # Override the options from ``raven.`` application settings.
    kwargs = defaults.copy()
    kwargs['context'] = context_data
    for k in settings:
        if k.startswith('raven.'):
            kwargs[k[6:]] = settings.get(k)
    return client_cls(**kwargs)

