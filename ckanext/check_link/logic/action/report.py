from __future__ import annotations
from typing import Any

from check_link import Link, check_all

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.lib.search.query import solr_literal

from ckanext.toolbelt.decorators import Collector

from ckanext.check_link.model import Report

from .. import schema

action, get_actions = Collector("check_link").split()


@action
@validate(schema.report_save)
def report_save(context, data_dict):
    tk.check_access("check_link_report_save", context, data_dict)
    sess = context["session"]
    data_dict["details"].update(data_dict.get("__extras", {}))

    try:
        existing = tk.get_action("check_link_report_show")(context, data_dict)
    except tk.ObjectNotFound:
        report = Report({**data_dict, "id": None})
        sess.add(report)
    else:
        report = sess.query(Report).filter(Report.id == existing["id"]).one()
        for k, v in data_dict.items():
            if k == "id":
                continue
            setattr(report, k, v)

    sess.commit()

    return report.dictize(context)
@action
@validate(schema.report_show)
def report_show(context, data_dict):
    tk.check_access("check_link_report_show", context, data_dict)

    if "id" in data_dict:
        report = context["session"].query(Report).filter(Report.id == data_dict["id"]).one_or_none()
    elif "resource_id" in data_dict:
        report = Report.by_resource_id(data_dict["resource_id"])
    elif "url" in data_dict:
        report = Report.by_url(data_dict["url"])
    else:
        raise tk.ValidationError({"id": ["One of the following must be provided: id, resource_id, url"]})

    if not report:
        raise tk.ObjectNotFound("Report not found")

    return report.dictize(context)

@action
@validate(schema.report_search)
def report_search(context, data_dict):
    tk.check_access("check_link_report_search", context, data_dict)



@action
@validate(schema.report_delete)
def report_delete(context, data_dict):
    tk.check_access("check_link_report_delete", context, data_dict)
    sess = context["session"]
    report = tk.get_action("check_link_report_show")(context, data_dict)
    entity = sess.query(Report).filter(Report.id == report["id"]).one()

    sess.delete(entity)
    sess.commit()
    return report.dictize(context)
