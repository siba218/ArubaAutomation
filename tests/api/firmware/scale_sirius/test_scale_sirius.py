from libs.api.FirmwareServices.firmware_api import FirmwareApi
from libs.utils.RestFrontEnd import RestFrontEnd
from tests.api.group_management.base_group_management_test import GroupManagementTestBase


class SiriusScaleTest(GroupManagementTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.email = cls.aruba_automation_config.get_property("user", "email")
        cls.password = cls.aruba_automation_config.get_property("user", "password")
        cls.login_url = cls.aruba_automation_config.get_property("central", "login_url")
        cls.customer_id = cls.aruba_automation_config.get_property("user", "customer_id")
        cls.session = RestFrontEnd(host=cls.login_url, user=cls.email, password=cls.password,
                                   customer_id=cls.customer_id)

    def setUp(self):
        pass

    def test_move_devices(self):
        """
        switch_scale_500 - gr_id-26380 - 511 devices - TMPLT_GRP_(0-130)
        switch_scale_1000 - gr_id-26381 - 1039 devices-  TMPLT_GRP_(130-390)
        switch_scale_1000_1 - gr_id-26382 -
        """

        to_group_id = 26380
        for i in range(900, 920):
            group_id = self.get_groups_id(self.session, 1, "TMPLT_GRP_{}".format(i))
            self.log.printLog("group id: {}".format(group_id))
            if group_id is not None:
                devices = self.device_list_in_group(self.session, group_id, 30)
                self.assign_devices_to_group(self.session, to_group_id, devices)

        # device_list = []
        # total_devices_count = 0
        # for group_id in group_ids_list:
        #     devices = self.device_list_in_group(self.session, group_id, 10)
        #     device_list.append(devices)
        #     total_devices_count = total_devices_count + len(devices)
        # self.log.printLog("devices_list : {}".format(device_list))
        # self.log.printLog("total number of devices to move : {}".format(total_devices_count))
        # self.assign_devices_to_group(self.session)

    def test_scale_upgrade(self):
        """
        {"reboot":true,"when":0,"timezone":"+00:00","partition":"primary","group":{"2":"16.10.0014"},"devices":{}}
        """
        version = "16.10.0014"
        payload1 = {"reboot": True, "when": 0, "timezone": "+00:00", "partition": "primary","group": {"26380": version}, "devices": {}}
        FirmwareApi().upgrade_all(self.session, data=payload1)

        payload2 = {"reboot": True, "when": 0, "timezone": "+00:00", "partition": "primary","group": {"26381": version}, "devices": {}}
        FirmwareApi().upgrade_all(self.session, data=payload2)

        payload3 = {"reboot": True, "when": 0, "timezone": "+00:00", "partition": "primary","group": {"26382": version}, "devices": {}}
        FirmwareApi().upgrade_all(self.session, data=payload3)
