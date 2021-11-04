# encoding: utf-8

import logging
import time


class Reporting():

    def __init__(self):
        self.log = logging.getLogger("ckanext.report.cli")

    def initdb(self):
        from ckanext.report import model
        model.init_tables()
        self.log.info('Report table is setup')

    def list(self):
        from ckanext.report.report_registry import ReportRegistry
        registry = ReportRegistry.instance()
        for plugin, report_name, report_title in registry.get_names():
            report = registry.get_report(report_name)
            date = report.get_cached_date()
            print('%s: %s %s' % (plugin, report_name,
                  date.strftime('%d/%m/%Y %H:%M') if date else '(not cached)'))

    def generate(self, report_list=None):
        from ckanext.report.report_registry import ReportRegistry
        timings = {}

        self.log.info("Running reports => %s", report_list)
        registry = ReportRegistry.instance()
        if report_list:
            for report_name in report_list:
                s = time.time()
                registry.get_report(report_name).refresh_cache_for_all_options()
                timings[report_name] = time.time() - s
        else:
            s = time.time()
            registry.refresh_cache_for_all_reports()
            timings["All Reports"] = time.time() - s

        self.log.info("Report generation complete %s", timings)

    def generate_for_options(self, report_name, options):
        from ckanext.report.report_registry import ReportRegistry
        self.log.info("Running report => %s", report_name)
        registry = ReportRegistry.instance()
        report = registry.get_report(report_name)
        all_options = report.add_defaults_to_options(options,
                                                     report.option_defaults)
        report.refresh_cache(all_options)
