import json
import os
import re
from typing import NamedTuple, TypedDict

from paramiko import SSHClient, AutoAddPolicy


class OutlineJson(TypedDict):
    apiUrl: str
    certSha256: str


class Outline(NamedTuple):
    api_root: str
    json_string: OutlineJson


class RemoteCmdExecutor:
    def __init__(self, password: str, host: str = 'localhost', port: int = 22, user: str = "root", ):
        self.__client = SSHClient()
        self.__client.set_missing_host_key_policy(AutoAddPolicy())
        self.__client.connect(hostname=host, port=port, username=user, password=password)

    def _remote_tmp_dir(self) -> str:
        _, stdout, _ = self.__client.exec_command("dirname $(mktemp -d)")
        lines = stdout.readlines()
        if len(lines) == 1:
            return lines[0].replace('\n', '')
        else:
            return ""

    def _get_os_info(self) -> (str, str):
        script = script = """
            if grep -qs "ubuntu" /etc/os-release; then
                echo "ubuntu"
                echo $(grep 'VERSION_ID' /etc/os-release | cut -d '"' -f 2 | tr -d '.')
            elif [[ -e /etc/debian_version ]]; then
                echo "debian"
                echo $(grep -oE '[0-9]+' /etc/debian_version | head -1)
            elif [[ -e /etc/almalinux-release || -e /etc/rocky-release || -e /etc/centos-release ]]; then
                echo "centos"
                echo $(grep -shoE '[0-9]+' /etc/almalinux-release /etc/rocky-release /etc/centos-release | head -1)
            elif [[ -e /etc/fedora-release ]]; then
                echo "fedora"
                echo $(grep -oE '[0-9]+' /etc/fedora-release | head -1)
            fi"""
        _, stdout, _ = self.__client.exec_command(script)
        lines = stdout.readlines()
        if len(lines) == 2:
            return (lines[0].replace('\n', ''), lines[1].replace('\n', ''))
        else:
            return ("None", "None")

    def execute_cmd(self, cmd: str):
        return self.__client.exec_command(cmd)

    def execute_bash_script(self, path: str, args: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File {path} not exists")
        ftp_client = self.__client.open_sftp()
        remote_path = os.path.join(self._remote_tmp_dir(), os.path.basename(path))
        ftp_client.put(path, remote_path)
        ftp_client.close()
        self.execute_cmd(f"chmod +x {remote_path}")
        print(f'chmod {remote_path}, run script')
        return self.execute_cmd(f"{remote_path} {args}")

    def release(self):
        self.__client.close()


class VPNDeployment:
    def __init__(self, remote_cmd_exec: RemoteCmdExecutor, client_count: int = 1):
        self.__client_count = client_count
        self.__remote_cmd_exec = remote_cmd_exec

    def get_client_count(self) -> int:
        return self.__client_count

    def get_client_conf(self, id: int):
        if id <= self.get_client_count():
            _, stdout, _ = self.__remote_cmd_exec.execute_cmd(f"cat /var/lib/wg/peer{id}/peer{id}.conf")
            return stdout.read()

    def get_client_qr(self, id: int):
        if id <= self.get_client_count():
            _, stdout, _ = self.__remote_cmd_exec.execute_cmd(f"cat /var/lib/wg/peer{id}/peer{id}.png")
            return stdout.read()

    def deploy(self, script_path: str) -> bool:
        _, stdout, stderr = self.__remote_cmd_exec.execute_bash_script(script_path, f"-n {self.__client_count}")
        try:
            with open('order/stdout.txt', 'w', encoding='utf-8') as file:
                file.writelines(stdout.readlines())
            with open('order/stderr.txt', 'w', encoding='utf-8') as file:
                file.writelines(stdout.readlines())
        except:
            pass
        return True

    def deploy_outline(self, script_path: str) -> Outline:
        _, stdout, stderr = self.__remote_cmd_exec.execute_bash_script(script_path, f"--api-port 8000 --keys-port 8001")
        stdout, stderr = stdout.readlines(), stderr.readlines()
        with open('order/stdout.txt', 'w', encoding='utf-8') as file:
            file.writelines(stdout)
        with open('order/stderr.txt', 'w', encoding='utf-8') as file:
            file.writelines(stdout)
        data = dict()
        for line in stdout:
            string = re.search(r'{"apiUrl":"https:.+","certSha256":".+"}', line)
            if string is not None:
                data = json.loads(string.group())
            _, stdout, stderr = self.__remote_cmd_exec.execute_cmd("systemctl disable firewalld --now")
            print(stdout.readlines())
        return Outline(data.get("apiUrl", None), data)


class MessengerDeployment:
    def __init__(self, remote_cmd_exec: RemoteCmdExecutor, user: str, password: str, domain: str):
        self.__remote_cmd_exec = remote_cmd_exec
        self.__user = user
        self.__password = password
        self.__domain = domain

    def deploy(self, script_path: str) -> bool:
        _, stdout, stderr = self.__remote_cmd_exec.execute_bash_script(script_path,
                                                                       f"-d {self.__domain} -e ivaneev.ivane@gmail.com -u {self.__user} -p {self.__password} -l")
        out_err = stderr.readlines()
        out = stdout.readlines()
        print(out, out_err)
        with open('orders/scripts/stdout.txt', 'w', encoding='utf-8') as file:
            file.writelines(out_err)
        with open('orders/scripts/stderr.txt', 'w', encoding='utf-8') as file:
            file.writelines(out)
        return True


if __name__ == '__main__':
    vpn = VPNDeployment(RemoteCmdExecutor(host='localhost', port=22000, user='root', password='210673'))
    print(f"DEBUG: vpn clinet count {vpn.get_client_count()}")
    if not vpn.deploy("./scripts/wg-install-helper"):
        print("Error: Installation has failed!")
    print(vpn.get_client_conf(1))
