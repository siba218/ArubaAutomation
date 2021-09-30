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
        # group_ids_list = self.get_groups_id_list(self.session, 20, "TMPLT_GRP")
        # self.log.printLog("group ids list: {}".format(group_ids_list))
        #
        # # create a dictionary  - {group_id:[device_list,]
        # data_dict = {}
        # for group_id  in group_ids_list:
        #     device_list = self.device_list_in_group(self.session, group_id, 10)
        #     data_dict[group_id] = device_list
        # self.log.printLog("final data list: {}".format(data_dict))
        self.assign_devices_to_group(self.session)

