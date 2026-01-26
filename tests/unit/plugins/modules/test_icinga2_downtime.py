# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
from pytest import importorskip

from ansible_collections.community.general.plugins.modules import icinga2_downtime

# Skip this test if icinga2apic cannot be installed
icinga2_api_client = importorskip("icinga2apic")


class TestIcinga2Downtime(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = icinga2_downtime

    def tearDown(self):
        super().tearDown()

    @patch("ansible_collections.community.general.plugins.modules.icinga2_downtime.Icinga2Client")
    def test_schedule_downtime(self, client_mock):
        with set_module_args(
            {
                "api_url": "http://localhost:5665",
                "api_version": "1",
                "api_user": "icingaadmin",
                "api_password": "secret",
                "state": "present",
                "start_time": 1769954400,
                "end_time": 1769958000,
                "duration": 3600,
                "fixed": True,
                "object_type": "Host",
                "filters": 'host.name=="test-host.local"',
            }
        ):
            response = {
                "results": [
                    {
                        "code": 200,
                        "legacy_id": 28911,
                        "name": "test-host.local!e19c705a-54c2-49c5-8014-70ff624f9e51",
                        "status": "Successfully scheduled downtime 'test-host.local!e19c705a-54c2-49c5-8014-70ff624f9e51' for object 'test-host.local'.",
                    }
                ]
            }
            schedule_downtime_mock = MagicMock(return_value=response)
            actions_mock = MagicMock(schedule_downtime=schedule_downtime_mock)
            client_mock.return_value = MagicMock(actions=actions_mock)

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(result.exception.args[0]["results"], response["results"])
        schedule_downtime_mock.assert_called_once_with(
            object_type=self.module.params["object_type"],
            filters=self.module.params["filters"],
            author=self.module.params["author"],
            comment=self.module.params["comment"],
            start_time=self.module.params["start_time"],
            end_time=self.module.params["end_time"],
            duration=self.module.params["duration"],
            fixed=self.module.params["fixed"],
        )

    @patch("ansible_collections.community.general.plugins.modules.icinga2_downtime.Icinga2Client")
    def test_remove_downtime(self, client_mock):
        with set_module_args(
            {
                "api_url": "http://localhost:5665",
                "api_version": "1",
                "api_user": "icingaadmin",
                "api_password": "secret",
                "state": "absent",
                "name": "test-host.local!e19c705a-54c2-49c5-8014-70ff624f9e51",
                "object_type": "Downtime",
            }
        ):
            response = {
                "results": [
                    {
                        "code": 200,
                        "status": "Successfully removed downtime 'test-host.local!e19c705a-54c2-49c5-8014-70ff624f9e51' and 0 child downtimes.",
                    }
                ]
            }
            remove_downtime_mock = MagicMock(return_value=response)
            actions_mock = MagicMock(remove_downtime=remove_downtime_mock)
            client_mock.return_value = MagicMock(actions=actions_mock)

            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()

        self.assertTrue(result.exception.args[0]["changed"])
        self.assertEqual(result.exception.args[0]["results"], response["results"])
        remove_downtime_mock.assert_called_once_with(
            object_type=self.module.params["object_type"],
            name=self.module.params["name"],
        )
