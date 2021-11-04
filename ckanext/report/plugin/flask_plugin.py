# encoding: utf-8

import ckan.plugins as p
from ckanext.report import views
from ckanext.report.cli import click_cli


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()

    # IClick

    def get_commands(self):
        return click_cli.get_commands()
