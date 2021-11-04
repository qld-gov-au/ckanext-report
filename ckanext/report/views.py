# encoding: utf-8

from flask import Blueprint

from ckanext.report.controllers import report_index, report_view
from ckan.plugins import toolkit


reporting = Blueprint(
    u'report',
    __name__
)


def redirect_to_index():
    return toolkit.redirect_to('/report')


reporting.add_url_rule(
    u'/report', view_func=report_index
)
reporting.add_url_rule(
    u'/reports', view_func=redirect_to_index
)
reporting.add_url_rule(
    u'/report/<report_name>', view_func=report_view
)
reporting.add_url_rule(
    u'/report/<report_name>/<organization>', view_func=report_view
)


def get_blueprints():
    return [reporting]
