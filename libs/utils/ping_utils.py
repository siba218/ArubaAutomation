import subprocess
import time

import paramiko


class PingDevice:
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

        key_file = "/Users/sibasishmohanta/.ssh/id_rsa"
        k = paramiko.RSAKey.from_private_key_file(key_file)

        print("connecting to the device...")
        ssh.connect(hostname=host, username=username, password=password, allow_agent=False, look_for_keys=False)
        time.sleep(5)
        print("Device Connected using ssh..")
        print("Invoking shell for executing command...")
        print("command list: {}".format(commands))
        out = []
        conn = ssh.invoke_shell()
        for cmd in commands:
            # print("#####################################################")
            cmd_bytes = cmd.encode("utf-8")
            conn.send(cmd_bytes)
            time.sleep(5)
            output = conn.recv(650000)
            if cmd == '\n':
                continue
            out.append(output.decode())
            # print(output.decode(), end='')
            # print('\n')
            # print("#####################################################", end='\n')
        ssh.close()
        return out


if __name__ == "__main__":
    # out11 = PingDevice().ping_once("10.21.31.166")
    # print("------------------")
    # print(out11)
    # PingDevice().ssh_jenkins_machine()
    command = ['\n', "sh version\n"]
    force_connect_yoda = ['\n', "config terminal\n", "aruba-central url https://device-yoda.arubathena.com/ws\n",
                          "aruba-central enable\n", "exit\n", "show aruba-central\n"]
    # PingDevice().ssh_device("10.22.108.82", "admin", "admin1234", ['\n', 'sh flash\n', 'sh version\n', 'exit\n'])
    l = PingDevice().ssh_device("10.22.108.82", "admin", "admin1234", command)
    print("#########################################")
    print(l)
    for item in l:
        print(item)
