import pytest

from ckan.plugins import plugin_loaded
from ckan.tests.helpers import call_action

from ckanext.check_link.model import Report


@pytest.mark.ckan_config("ckan.plugins", "check_link")
@pytest.mark.usefixtures("with_plugins")
def test_plugin():
    assert plugin_loaded("check_link")


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestCascadeReportRemoval:
    def test_not_removed_by_default(self, report):
        call_action("resource_delete", id=report["resource_id"])
        assert Report.by_resource_id(report["resource_id"])

    @pytest.mark.ckan_config(
        "ckanext.check_link.remove_reports_when_resource_deleted", "true"
    )
    def test_removed_if_configured(self, report):
        call_action("resource_delete", id=report["resource_id"])
        assert not Report.by_resource_id(report["resource_id"])

    @pytest.mark.ckan_config(
        "ckanext.check_link.remove_reports_when_resource_deleted", "true"
    )
    def test_removed_if_resource_dropped_via_package_update(self, report):
        resource = call_action("resource_show", id=report["resource_id"])
        call_action("package_patch", id=resource["package_id"], resources=[])

        assert not Report.by_resource_id(report["resource_id"])
