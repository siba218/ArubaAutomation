class GroupManagementRequest:
    def __init__(self):
        self.group_id = None
        self.devices = []


class GroupManagementRequestBuilder:
    def __init__(self):
        self.data = GroupManagementRequest()

    def with_group_id(self, group_id):
        self.data.group_id = group_id
        return self

    def with_devices(self, devices_list):
        self.data.devices = devices_list
        return self

    def build(self):
        return self.data.__dict__


