# encoding: utf-8

from flask import Blueprint

from ckanext.report.controllers import report_index, report_view
from ckan.plugins import toolkit


reporting = Blueprint(
    u'report',
    __name__,
    url_prefix=u'/report'
)
reporting_redirect = Blueprint(
    u'reports',
    __name__,
    url_prefix=u'/reports'
)


def redirect_to_index():
    return toolkit.redirect_to('/report')


reporting.add_url_rule(
    u'/', view_func=report_index
)
reporting.add_url_rule(
    u'/<report_name>', view_func=report_view
)
reporting.add_url_rule(
    u'/<report_name>/<organization>', view_func=report_view
)

reporting_redirect.add_url_rule(
    u'/', view_func=redirect_to_index
)


def get_blueprints():
    return [reporting]
