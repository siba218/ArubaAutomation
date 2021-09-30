from libs.api.FirmwareServices.firmware_api import FirmwareApi
from libs.api.GroupManagementServices.group_management_api import GroupManagementApi
from tests.base_universal_test import BaseUniversalTest


class GroupManagementTestBase(BaseUniversalTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_management = GroupManagementApi()
        cls.firmware = FirmwareApi()

    def get_groups_id_list(self, session, limit, group_name_contains):
        group_ids_list = []
        params = {}
        params["group_name"] = group_name_contains
        resp = self.group_management.get_groups(session, limit=limit, params=params)
        for group in resp.body["groups"]:
            group_ids_list.append(group["groupid"])
        return group_ids_list

    def device_list_in_group(self, session, group_id, limit):
        device_serial_list = []
        resp = self.firmware.get_devices_in_group(session, group_id, limit=limit)
        for device in resp.body["device_info"]:
            device_serial_list.append(device["device_id"])
        return device_serial_list

    def assign_devices_to_group(self, session):
        data = {"group_id": 26380, "devices": ['IITB010019', 'IITB010020', 'LEYY000037', 'LEYY000039']}
        self.group_management.assign_devices_to_group(session, data=data)
