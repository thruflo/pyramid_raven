# -*- coding: utf-8 -*-

"""Panel view for the ``raven-js`` panel."""

__all__ = [
    'raven_js_panel'
]

import logging
logger = logging.getLogger(__name__)

import os
import re
import urlparse

from pyramid.path import DottedNameResolver

from .constants import DEFAULT_RAVEN_JS_SRC

def to_escaped_host_path(url):
    r"""Take the netloc of a url and escape it::
      
          >>> url = 'http://www.cwi.nl:80/%7Eguido/Python.html'
          >>> to_escaped_host_path(url)
          'www\\.cwi\\.nl\\:80\\/\\%7Eguido\\/Python\\.html'
      
      Strips off any query string::
      
          >>> url = 'http://localhost:5100/?foo=bar'
          >>> to_escaped_host_path(url)
          'localhost\\:5100\\/'
      
      Works for urls that are actually just hosts::
      
          >>> url = 'google.com/foo'
          >>> to_escaped_host_path(url)
          'google\\.com\\/foo'
      
    """
    
    o = urlparse.urlparse(url)
    return re.escape(o.netloc) + re.escape(o.path)

def to_public_dsn(url):
    """Removes the basicauth password from a dsn url::
        
          >>> dsn = 'https://user:password@app.getsentry.com/1'
          >>> to_public_dsn(dsn)
          'https://user@app.getsentry.com/1'
      
      Works with schemeless urls too::
      
          >>> dsn = '//user:password@app.getsentry.com/1'
          >>> to_public_dsn(dsn)
          '//user@app.getsentry.com/1'
      
      Passes through urls without a `@`::
      
          >>> to_public_dsn('//user:password.app.getsentry.com/1')
          '//user:password.app.getsentry.com/1'
      
    """
    
    # Split the url on the `@`.
    parts = url.split('@')
    if len(parts) < 2:
        return url
    
    # Split the first part on `:`.
    subparts = parts[0].split(':')
    
    # If two parts and `//` isn't in the last part, we found a password.
    if len(subparts) > 1 and not '//' in subparts[-1]:
        # So strip it out.
        parts[0] = ':'.join(subparts[:-1])
    
    # Rebuild the url.
    return '@'.join(parts)


def raven_js_panel(context, request, env=None, to_host_path=None, to_public=None):
    r"""Provide data for the site search panel.
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_request.application_url = 'https://getsentry.com/'
          >>> mock_request.registry.settings = {}
          >>> mock_env = {'SENTRY_DSN': 'https://user:password@app.getsentry.com/1'}
          >>> vars = raven_js_panel(None, mock_request, env=mock_env)
          >>> vars['dsn']
          'https://user@app.getsentry.com/1'
          >>> vars['hosts']
          ['getsentry\\.com\\/']
          >>> assert vars['src'] == DEFAULT_RAVEN_JS_SRC
      
      If the settings specify an ``assetgen.serving_path`` and / or
      any ``pyramid_raven.include_hosts`` then they're added to the ``hosts``::
      
          >>> mock_request.registry.settings = {
          ...       'assetgen.serving_path': '//foo.com',
          ...       'pyramid_raven.include_hosts': 'baz.com bar.net'
          ... }
          >>> vars = raven_js_panel(None, mock_request, env=mock_env)
          >>> vars['hosts']
          ['getsentry\\.com\\/', 'foo\\.com', 'baz\\.com', 'bar\\.net']
      
      As per urls returned by a factory specified as a dotted path::
      
          >>> from pyramid_raven import panel
          >>> panel.doctest_include_hosts_factory = lambda r: ['blob.io']
          >>> mock_request.registry.settings = {
          ...       'pyramid_raven.include_hosts_factory': \
          ...       'pyramid_raven.panel.doctest_include_hosts_factory'
          ... }
          >>> vars = raven_js_panel(None, mock_request, env=mock_env)
          >>> vars['hosts']
          ['getsentry\\.com\\/', 'blob\\.io']
          >>> del panel.doctest_include_hosts_factory
      
    """
    
    # Compose.
    if env is None:#pragma: no cover
        env = os.environ
    if to_host_path is None:#pragma: no cover
        to_host_path = to_escaped_host_path
    if to_public is None:#pragma: no cover
        to_public = to_public_dsn
    
    # Unpack.
    settings = request.registry.settings
    sentry_dsn = env['SENTRY_DSN']
    strip = lambda s: s.strip()
    
    # Get the raven javascript ``src`` url.
    src = settings.get('pyramid_raven.raven_js_src', DEFAULT_RAVEN_JS_SRC)
    
    # Parse the ``dsn`` into a version without the password.
    dsn = to_public(sentry_dsn)
    
    # Build the ``hosts`` list of re.escaped ``netloc + /paths``.
    urls = [request.application_url]
    assets_url = settings.get('assetgen.serving_path', None)
    if assets_url:
        urls.append(assets_url)
    include_hosts = settings.get('pyramid_raven.include_hosts')
    if include_hosts: # if we've been given a list of extra hosts...
        urls += map(strip, include_hosts.split(' '))
    include_hosts_factory = settings.get('pyramid_raven.include_hosts_factory')
    if include_hosts_factory: # if a dotted path to a factory function...
        factory = DottedNameResolver().resolve(include_hosts_factory)
        urls += factory(request)
    hosts = map(to_host_path, urls)
    
    # Pass the values through to the panel template.
    return {
        'dsn': dsn,
        'hosts': hosts,
        'src': src,
    }

