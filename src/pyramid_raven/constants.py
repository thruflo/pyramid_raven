# -*- coding: utf-8 -*-

"""Constant values."""

ATTR_METHODS = [
    'geoip',
]
ATTR_PROPERTIES = [
    'context',
    'geodata',
    'layout_manager',
    'matchdict',
    'matched_route',
    'root',
    'subpath',
    'traversed',
    'view_name',
    'virtual_root',
    'virtual_root_path'
]
DEFAULT_CLIENT_KWARGS = {
    'processors': (
        'raven.processors.SanitizePasswordsProcessor',
        'raven.processors.RemovePostDataProcessor',
    ),
    'timeout': 4,
}
DEFAULT_RAVEN_JS_SRC = '//d3nslu0hdya83q.cloudfront.net/dist/1.0/raven.min.js'