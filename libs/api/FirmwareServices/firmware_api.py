class FirmwareApi:
    def __init__(self, session, env=None):
        self.session = session
        self.base_url = self.session.host

    def get_devices_down_status(self, params=None):
        response = self.session.get(self.base_url + "monitor/v2/switches", params=params)
        return response

    def create_group(self, data=None, params=None):
        resp = self.session.post(self.session.host + "groups/v2", data=data)
        return resp

    def delete_group(self, group_id, data=None, params=None):
        response = self.session.delete(self.session.host + "groups/v2/{}".format(group_id))
        return response

    def get_switch_list_details(self):
        response = self.session.get(self.session.host + "firmware/switch/HPPC/devices/limit/20/offset/0")
        return response

    def upgrade_all(self, data=None):
        response = self.session.post(self.session.host + "firmware/switch/HPPC/upgrade", data=data)
        return response
