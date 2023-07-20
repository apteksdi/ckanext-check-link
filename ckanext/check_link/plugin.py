from __future__ import annotations

from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan import model

from . import cli, helpers, views
from .logic import action, auth
from .model import Report

CONFIG_CASCADE_DELETE = "ckanext.check_link.remove_reports_when_resource_deleted"


class CheckLinkPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)

    def notify(self, entity: Any, operation: str) -> None:
        if isinstance(entity, model.Resource) and entity.state == "deleted":
            if toolkit.asbool(toolkit.config.get(CONFIG_CASCADE_DELETE)):
                _remove_resource_report(entity.id)

    # ITemplateHelpers

    def get_helpers(self):
        return helpers.get_helpers()

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "check_link")

    # IActions
    def get_actions(self):
        return action.get_actions()

    # IAuthFunctions
    def get_auth_functions(self):
        return auth.get_auth_functions()

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprints()

    # IClick
    def get_commands(self):
        return cli.get_commands()


def _remove_resource_report(resource_id: str):
    report = Report.by_resource_id(resource_id)
    if report:
        model.Session.delete(report)
