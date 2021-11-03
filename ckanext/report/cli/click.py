# encoding: utf-8

import click

from ckanext.report.cli.command import Reporting

# Click commands for CKAN 2.9 and above


@click.group()
def report():
    """ XLoader commands
    """
    pass


@report.command()
def list():
    """ Lists the reports
    """
    cmd = Reporting()
    cmd.list()


@report.command()
def initdb():
    """ Initialize the database tables for this extension
    """
    cmd = Reporting()
    cmd.initdb()


@report.command()
@click.argument(u'report_names')
def generate(report_names):
    """
    Generate and cache reports - all of them unless you specify
    a comma separated list of them.
    """
    cmd = Reporting()
    report_list = [s.strip() for s in report_names.split(',')]
    cmd.generate(report_list)


@report.command()
@click.argument(u'report_name')
@click.argument(u'options', nargs=-1)
def generate_for_options(report_name, options):
    """
    Generate and cache a report for one combination of option values.
    You can leave it with the defaults or specify options
    as more parameters: key1=value key2=value
    """
    cmd = Reporting()
    report_options = {}
    for option_arg in options:
        if '=' not in option_arg:
            raise click.BadParameter(
                'Option needs an "=" sign in it',
                options)
        equal_pos = option_arg.find('=')
        key, value = option_arg[:equal_pos], option_arg[equal_pos + 1:]
        if value == '':
            value = None  # this is what the web i/f does with params
        report_options[key] = value
    cmd.generate_for_options(report_name, report_options)


def get_commands():
    return [report]
