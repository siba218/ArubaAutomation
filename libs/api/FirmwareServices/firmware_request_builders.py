"""
{"reboot":true,"when":0,"timezone":"+00:00","partition":"primary","group":{"":"16.10.0014"},"devices":{}}
{"reboot":true,"when":0,"timezone":"+00:00","partition":"primary","sites":{"1":"16.09.0016","35":"16.09.0016"},"devices":{}}

"""
class Device:
    def __init__(self):
        self.devices = {}

class Group:
    def __init__(self):
        self.group = {}

class GroupRequestBuilder:
    def __init__(self):
        pass


class FirmwareUpgradeRequest:
    def __init__(self):
        self.devices = {}
        self.reboot = True
        self.when = 0
        self.timezone = "+00:00"
        self.partition = "primary"

class FirmwareUpgradeRequestBuilder:
    def __init__(self):
        self.data = FirmwareUpgradeRequest()

    def with_reboot(self, boot_type):
        self.data.reboot = boot_type
        return self

    def with_when(self, time):
        self.data.when = time
        return self

    def build(self):
        return self.data.__dict__

if __name__ == "__main__":
    print(FirmwareUpgradeRequestBuilder().with_reboot(False).build())
