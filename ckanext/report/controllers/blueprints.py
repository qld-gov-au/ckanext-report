# encoding: utf-8

import six

from flask import Blueprint, Response

from ckan.plugins import toolkit
from . import report_index, report_view


reporting = Blueprint(
    u'report',
    __name__
)


def redirect_to_index():
    return toolkit.redirect_to('/report')


def view(report_name, organization=None, refresh=False):
    body, headers = report_view(report_name, organization, refresh)
    if headers:
        response = Response(body)
        for key, value in six.iteritems(headers):
            response.headers[key] = value
        return response
    else:
        return body


reporting.add_url_rule(
    u'/report', 'index', view_func=report_index
)
reporting.add_url_rule(
    u'/reports', 'reports', view_func=redirect_to_index
)
reporting.add_url_rule(
    u'/report/<report_name>', 'view', view_func=view, methods=('GET', 'POST',)
)
reporting.add_url_rule(
    u'/report/<report_name>/<organization>', 'org', view_func=view, methods=('GET', 'POST',)
)


def get_blueprints():
    return [reporting]
