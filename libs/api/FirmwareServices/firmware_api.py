class FirmwareApi:

    def get_devices_down_status(self, session, params=None):
        response = session.get(session.host + "monitor/v2/switches", params=params)
        return response

    def create_group(self, session, data=None, params=None):
        resp = session.post(session.host + "groups/v2", data=data)
        return resp

    def delete_group(self, session, group_id, data=None, params=None):
        response = session.delete(session.host + "groups/v2/{}".format(group_id))
        return response

    def get_switch_list_details(self, session ):
        response = session.get(session.host + "firmware/switch/HPPC/devices/limit/20/offset/0")
        return response

    def upgrade_all(self, session, data=None):
        response = session.post(session.host + "firmware/switch/HPPC/upgrade", data=data)
        return response

    def device_reboot(self, session, data=None):
        response = session.post(session.host + "firmware/switch/HPPC/reboot", data=data)
        return response

    def set_group_compliance_check(self, session, data=None):
        response = session.post(session.host + "firmware/group/compliance_version_check", data=data)
        return response

    def set_group_compliance(self, session, data=None):
        response = session.post(session.host + "firmware/group/compliance_version", data=data)
        return response

    def get_devices_in_group(self, session, group_id, limit=1, params=None):
        response = session.get(
            session.host + "firmware/switch/HPPC/group/{}/devices/limit/{}/offset/0".format(group_id, limit))
        return response
