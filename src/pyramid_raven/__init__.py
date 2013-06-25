#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides an ``includeme`` function that lets developers configure the
  package to be part of their Pyramid application with::
  
      config.include('pyramid_raven')
  
"""

from .client import get_raven_client
from .panel import raven_js_panel

def includeme(config, get_raven=None, panel=None):
    """Add the ``request.raven`` method and configure the `raven-js` panel.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_config = Mock()
          >>> mock_config.registry.settings = {}
          >>> mock_get_raven = Mock()
          >>> mock_panel = Mock()
          >>> includeme(mock_config, get_raven=mock_get_raven, panel=mock_panel)
      
      Adds the request method::
      
          >>> mock_config.add_request_method.assert_called_with(mock_get_raven,
          ...         'raven', reify=True)
      
      Configures the panel::
      
          >>> mock_config.add_panel.assert_called_with(mock_panel, 'raven-js',
          ...         renderer='pyramid_raven:templates/panel.mako')
      
      Using the ``pyramid_raven.panel_tmpl`` setting if provided::
      
          >>> mock_config.registry.settings = {
          ...     'pyramid_raven.panel_tmpl': 'mypkg:templates/foo.tmpl'
          ... }
          >>> includeme(mock_config, get_raven=mock_get_raven, panel=mock_panel)
          >>> mock_config.add_panel.assert_called_with(mock_panel, 'raven-js',
          ...         renderer='mypkg:templates/foo.tmpl')
      
    """
    
    # Compose.
    if get_raven is None: #pragma: no cover
        get_raven = get_raven_client
    if panel is None: #pragma: no cover
        panel = raven_js_panel
    
    # Unpack.
    settings = config.registry.settings
    
    # Provide the client as ``request.raven``.
    config.add_request_method(get_raven, 'raven', reify=True)
    
    # Configure the ``raven-js`` panel.
    default_tmpl = 'pyramid_raven:templates/panel.mako'
    panel_tmpl = settings.get('pyramid_raven.panel_tmpl', default_tmpl)
    config.add_panel(panel, 'raven-js', renderer=panel_tmpl)

