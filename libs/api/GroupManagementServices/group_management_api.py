class GroupManagementApi:

    def get_groups(self, session, limit=1, params=None):
        response = session.get(session.host + "groups/v2/limit/{}/offset/0".format(limit), params=params)
        return response

    def assign_devices_to_group(self, session, data=None):
        response = session.post(session.host + "groups/v2/assign", data=data)
        return response
