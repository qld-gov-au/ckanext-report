# encoding: utf-8

import ckan.plugins.toolkit as t
from ckanext.report.controllers import report_index, report_view


class ReportController(t.BaseController):

    def index(self):
        return report_index()

    def view(self, report_name, organization=None, refresh=False):
        return report_view(report_name, organization, refresh)
