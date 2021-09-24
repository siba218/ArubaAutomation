"""
UpgradeAll:
{"reboot":true,"when":0,"timezone":"+00:00","partition":"primary","group":{"":"16.10.0014"},"devices":{}}
{"reboot":true,"when":0,"timezone":"+00:00","partition":"primary","sites":{"1":"16.09.0016","35":"16.09.0016"},"devices":{}}

SetCompliance:
{"delete_firmware_compliance":{},"set_firmware_compliance":{"HPPC":"16.10.0015"},"reboot":{"HPPC":true},"groups":[3],
"compliance_scheduled_at":0,"timezone":"+00:00","partition":"primary"}

Individual Device Upgrade:
{"reboot":true,"when":0,"timezone":"+00:00","partition":"primary","devices":{"CN80HKW005":"16.10.0014"}}
"""


class FirmwareUpgradeAllRequest:
    def __init__(self):
        self.devices = {}
        self.reboot = True
        self.when = 0
        self.timezone = "+00:00"
        self.partition = "primary"
        self.sites = {}


class FirmwareUpgradeAllRequestBuilder:
    def __init__(self):
        self.data = FirmwareUpgradeAllRequest()

    def with_reboot(self, boot_type):
        self.data.reboot = boot_type
        return self

    def with_when(self, time):
        self.data.when = time
        return self

    def with_sites(self, site_dict):
        self.data.sites = site_dict
        return self

    def with_timezone(self, timezone):
        self.data.timezone = timezone
        return self

    def build(self):
        return self.data.__dict__


class FirmwareComplianceRequest:
    def __init__(self):
        self.delete_firmware_compliance = {}
        self.set_firmware_compliance = {}
        self.reboot = {"HPPC": True}
        self.groups = []
        self.compliance_scheduled_at = 0
        self.timezone = "+00:00"
        self.partition = "primary"


class FirmwareComplianceRequestBuilder:
    def __init__(self):
        self.data = FirmwareComplianceRequest()

    def with_delete_firmware_compliance(self, delete_compliance):
        self.data.delete_firmware_compliance = delete_compliance
        return self

    def with_set_firmware_compliance(self, set_compliance):
        self.data.set_firmware_compliance = set_compliance
        return self

    def with_reboot(self, hppc_reboot):
        self.data.reboot = hppc_reboot
        return self

    def with_groups(self, groups_list):
        self.data.groups = groups_list
        return self

    def with_compliance_scheduled_at(self, schedule_epoch_time):
        self.data.compliance_scheduled_at = schedule_epoch_time
        return self

    def with_timezone(self, timezone):
        self.data.timezone = timezone
        return self

    def with_partition(self, partition):
        self.data.partition = partition
        return self

    def build(self):
        return self.data.__dict__


class FirmwareDeviceRequest:
    def __init__(self):
        self.devices = {}
        self.reboot = True
        self.when = 0
        self.timezone = "+00:00"
        self.partition = "primary"


class FirmwareDeviceRequestBuilder:
    def __init__(self):
        self.data = FirmwareDeviceRequest()

    def with_devices(self, device_list):
        self.data.devices = device_list
        return self

    def with_reboot(self, reboot):
        self.data.reboot = reboot
        return self

    def with_when(self, epoch_time):
        self.data.when = epoch_time
        return self

    def with_timezone(self, timezone):
        self.data.timezone = timezone
        return self

    def with_partition(self, partition):
        self.data.partition = partition
        return self

    def build(self):
        return self.data.__dict__


if __name__ == "__main__":
    print(FirmwareComplianceRequestBuilder().with_reboot({'HPPC':False}).build())
