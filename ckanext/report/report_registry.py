import logging
import copy
import re
import six

from paste.deploy.converters import asbool

from ckan import model
from ckan.common import OrderedDict
from ckanext.report.interfaces import IReport

log = logging.getLogger(__name__)

REPORT_KEYS_REQUIRED = set(('name', 'generate', 'template', 'option_defaults',
                            'option_combinations'))
REPORT_KEYS_OPTIONAL = set(('title', 'description', 'authorize'))


class Report(object):
    '''Represents a report that can be generated. Instances are generated by
    ReportRegistry.'''
    def __init__(self, report_info_dict, plugin):

        # Check the report_info_dict has the correct keys
        missing_required_keys = REPORT_KEYS_REQUIRED - set(report_info_dict.keys())
        assert not missing_required_keys, 'Report info dict missing keys %r: '\
            '%r' % (missing_required_keys, report_info_dict)
        unknown_keys = set(report_info_dict.keys()) - REPORT_KEYS_REQUIRED - \
            REPORT_KEYS_OPTIONAL
        assert not unknown_keys, 'Report info dict has unrecognized keys %r: '\
            '%r' % (unknown_keys, report_info_dict)
        if not report_info_dict['option_defaults']:
            report_info_dict['option_defaults'] = OrderedDict()
        assert isinstance(report_info_dict['option_defaults'], OrderedDict)

        # Save the required keys
        for key in REPORT_KEYS_REQUIRED:
            setattr(self, key, report_info_dict[key])
        self.plugin = plugin

        # Save the optional keys or their defaults
        for key in REPORT_KEYS_OPTIONAL:
            if key in report_info_dict:
                setattr(self, key, report_info_dict[key])
            elif key == 'title':
                self.title = re.sub('[_-]', ' ', self.name.capitalize())
            elif key == 'description':
                self.description = ''

    def generate_key(self, option_dict, defaults_for_missing_keys=True):
        '''Returns a key that will identify the report and options when saved
        in the DataCache. It looks like URL parameters for convenience.'''
        options_serialized = []
        for key in self.option_defaults:
            if defaults_for_missing_keys:
                value = option_dict.get(key,
                                        self.option_defaults[key])
            else:
                value = option_dict[key]
            if isinstance(value, six.string_types):
                try:
                    value = six.binary_type(value)
                except UnicodeEncodeError:
                    value = value.encode('utf8')
            elif isinstance(value, bool):
                value = 1 if value else 0
            else:
                value = repr(value)
            option = '%s=%s' % (key, value)
            options_serialized.append(option)
        if options_serialized:
            return '%s?%s' % (self.name, '&'.join(options_serialized))
        else:
            return '%s' % self.name

    def refresh_cache_for_all_options(self):
        '''Generates the report for all the option combinations and caches them.'''
        log.info('Report: %s %s', self.plugin, self.name)
        option_combinations = list(self.option_combinations()) \
            if self.option_combinations else [{}]
        for option_dict in option_combinations:
            self.refresh_cache(option_dict)
        log.info('  report done')

    def refresh_cache(self, option_dict):
        '''Generates a report for the given options and caches it.

        Returns (data, date)
        '''
        from ckanext.report import model as report_model
        log.info('  Gen for options: %r', option_dict)
        data = self.generate(**option_dict)
        # option_combinations should specify every key, so mustn't allow
        # default values
        key = self.generate_key(option_dict, defaults_for_missing_keys=False)
        date = report_model.DataCache.set(extract_entity_name(option_dict),
                                          key, data, convert_json=True)
        model.Session.commit()
        return data, date

    def get_fresh_report(self, **option_dict):
        from ckanext.report import model as report_model
        entity_name = extract_entity_name(option_dict)
        key = self.generate_key(option_dict)
        data, date = report_model.DataCache.get_if_fresh(
            entity_name, key, convert_json=True)
        if data is None:
            data, date = self.refresh_cache(option_dict)
        return data, date

    def get_cached_date(self, **option_dict):
        from ckanext.report import model as report_model
        if not option_dict:
            option_dict = self.option_defaults
        entity_name = extract_entity_name(option_dict)
        key = self.generate_key(option_dict)
        data, date = report_model.DataCache.get(entity_name, key)
        return date

    def get_template(self):
        return self.template

    @staticmethod
    def add_defaults_to_options(options, defaults):
        '''Returns the options, using option values passed in and falling back
        to the default values for that report.

        When a option needs a boolean, an option passed in as 0 or 1 are
        converted to True/False, which suits when the options passed in are URL
        parameters.
        '''
        defaulted_options = copy.deepcopy(defaults)
        for key in defaulted_options:
            if key not in options:
                if defaulted_options[key] is True:
                    # Checkboxes don't submit a value when False, so cannot
                    # default to True. i.e. to get a True value, you always
                    # need be expicit in the params.
                    defaulted_options[key] = False
                continue
            value = options[key]
            if isinstance(defaulted_options[key], bool):
                try:
                    defaulted_options[key] = asbool(value)
                except ValueError:
                    pass  # leave it as default
            else:
                defaulted_options[key] = value
        for key in set(options) - set(defaulted_options):
            defaulted_options[key] = options[key]
        return defaulted_options

    def as_dict(self):
        return {'name': self.name,
                'title': self.title,
                'description': self.description,
                'option_defaults': self.option_defaults,
                'template': self.get_template()}

    def is_visible_to_user(self, user):
        if hasattr(self, 'authorize'):
            return self.authorize(user, self.option_defaults)
        else:
            return True


def extract_entity_name(option_dict):
    '''Hunts for an option key that is the entity name and returns its
    value. Used in the DataCache storage.'''
    for entity_name in ('organization', 'publisher', 'group', 'package', 'resource'):
        if entity_name in option_dict:
            return option_dict[entity_name]
    return None


class ReportRegistry(object):
    _instance = None
    _reports = {}  # name: report

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # register all the reports
        import ckan.plugins as p
        self._reports = {}  # this reset is needed for 'paster serve --restart'
        for plugin in p.PluginImplementations(IReport):
            report_info_dicts = plugin.register_reports()
            for report_info_dict in report_info_dicts:
                assert report_info_dict['name'] not in self._reports, \
                    'Duplicate report name %s' % report_info_dict['name']
                plugin_name = '%s (%s)' % (plugin.__class__.__name__,
                                           plugin.name)
                self._reports[report_info_dict['name']] = \
                    Report(report_info_dict, plugin_name)

    def get_names(self):
        return [(r.plugin, r.name, r.title)
                for r in sorted(self._reports.values(), key=lambda r: r.plugin)]

    def get_reports(self):
        return sorted(self._reports.values(), key=lambda r: r.title)

    def get_report(self, report_name):
        return self._reports[report_name]

    def refresh_cache_for_all_reports(self):
        '''Generates all the reports for all the option combinations and caches them.'''
        for report in self._reports.values():
            report.refresh_cache_for_all_options()


#    'name': 'feedback-report',
#    'option_combinations': nii_report_combinations,
#    'generate': nii_report,
