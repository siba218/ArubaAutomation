import subprocess
import time

import paramiko

from libs.utils.customer_logger import CustomLogger


class PingUtils:
    def __init__(self):
        self.log = CustomLogger()
        self.log.setup_logger()

    def ping_once(self, host):
        command = ['ping', '-c', '1', host]
        return subprocess.call(command)

    def verify_device_online_with_ping(self, time=5, interval=10):
        pass

    def ssh_jenkins_machine(self):
        # host = "10.21.31.166"
        host = "10.21.22.39"
        # port = 22
        username = "blr-reg-jenkins"
        # username = "admin"
        password = "smokeprod"
        # password = "admin1234"

        command = "ls -1"
        # command = "sh flash"
        key_file = "/Users/sibasishmohanta/.ssh/id_rsa"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        k = paramiko.RSAKey.from_private_key_file(key_file)
        ssh.connect(host, username=username, password=password, pkey=k, allow_agent=False, look_for_keys=False)

        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        print(lines)
        stdin.close()
        stdout.close()
        stderr.close()
        ssh.close()

    def ssh_device(self, host, username, password, commands):
        # before using this you need to set username and password for your switch using below process
        """
        Note: Before running below commands unlicense the device from central
        Connect to the device using ssh
        Config terminal
        Password manager user-name admin
        >> it will ask for the password
        >> confirm the password
        write memory
        """
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # key_file = "/Users/sibasishmohanta/.ssh/id_rsa"
        # k = paramiko.RSAKey.from_private_key_file(key_file)

        self.log.printLog("connecting to the device...")
        try:
            ssh.connect(hostname=host, username=username, password=password, allow_agent=False, look_for_keys=False)
            time.sleep(5)
            self.log.printLog("Device Connected using ssh..")
            self.log.printLog("Invoking shell for executing command...")
            self.log.printLog("command list: {}".format(commands))
            out = []
            conn = ssh.invoke_shell()
            for cmd in commands:
                cmd_bytes = cmd.encode("utf-8")
                conn.send(cmd_bytes)
                time.sleep(5)
                output = conn.recv(650000)
                if cmd == '\n':
                    continue
                out.append(output.decode())
            ssh.close()
            return out
        except:
            self.log.printLog(
                "Device Connection using SSH failed."
                "Please Set Group level username: admin and password: admin1234 and retry")

    def get_device_details_using_ssh(self, host, username, password):
        command = ['\n', "sh flash\n"]
        std_out = PingUtils().ssh_device(host, username, password, command)
        device_data = {}
        for item in std_out[0].split('\n'):
            if "Primary Image" in item:
                device_data["primary_image"] = str(item).split()[-1]
            if "Secondary Image" in item:
                device_data["secondary_image"] = str(item).split()[-1]
            if "Default Boot Image" in item:
                device_data["default_boot_image"] = str(item).split()[-1]
        if device_data["default_boot_image"] == "Secondary":
            device_data["device_current_version"] = device_data["secondary_image"]
        elif device_data["default_boot_image"] == "Primary":
            device_data["device_current_version"] = device_data["primary_image"]
        device_data["current_version"] = device_data["device_current_version"][3:]
        return device_data


# if __name__ == "__main__":
#     data = PingUtils().get_device_details_using_ssh("10.21.31.166", "admin", "admin1234")
#     print("data is :{}".format(data))
    # PingDevice().testing()
    # out11 = PingDevice().ping_once("10.21.31.166")
    # print("------------------")
    # print(out11)
    # PingDevice().ssh_jenkins_machine()
    # command = ['\n', "sh system\n"]
    # force_connect_yoda = ['\n', "config terminal\n", "aruba-central url https://device-yoda.arubathena.com/ws\n",
    #                       "aruba-central enable\n", "exit\n", "show aruba-central\n"]
    # # PingDevice().ssh_device("10.22.108.82", "admin", "admin1234", ['\n', 'sh flash\n', 'sh version\n', 'exit\n'])
    # l = PingDevice().ssh_device("10.21.31.166", "admin", "admin1234", command)
    # print("#########################################")
    # print(l)
    # for item in l:
    #     print(item)
