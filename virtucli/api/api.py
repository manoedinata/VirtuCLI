from requests import Session
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

import logging

class Api(object):
    def __init__(self, server_url: str, api_key: str, api_password: str) -> None:
        # Base URL
        self.BASE_URL = server_url

        # Setup session
        self.session = Session()
        self.session.verify = False
        disable_warnings(InsecureRequestWarning)
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }

        # Base params
        # API & authentication params preparation
        self.base_params = {
            "api": "json",
            "apikey": api_key,
            "apipass": api_password,
            "do": 1
        }


    def __request(self, method: str, params_dict: dict, data_dict: dict = None) -> dict:
        """
        Make a request to API with automatic parameter handling.
        Handles network and HTTP errors gracefully.
        :param method: Request method
        :param params_dict: Required parameters, in dictionary
        :param data_dict: Data dictionary for POST requests
        """
        params = self.base_params.copy()
        params.update(params_dict)
        if data_dict is None:
            data_dict = {}
        try:
            resp = self.session.request(method=method, url=self.BASE_URL, params=params, data=data_dict, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.error(f" API request failed: {e}")
            return {"error": str(e)}

    # Functions: List VM
    def list_vm(self) -> list:
        """
        List VMs in an account.
        """
        return self.__request("GET", {"act": "listvs"})

    # Functions: VM info
    def vm_info(self, vps_id: int) -> dict:
        """
        Get specific VM information.
        :param vps_id: VPS ID number
        """
        return self.__request("GET", {"act": "vpsmanage", "svs": int(vps_id)})

    # Functions: Start VM
    def start_vm(self, vps_id: int) -> dict:
        """
        Start a specific VM.
        :param vps_id: VPS ID number
        """
        return self.__request("GET", {"act": "start", "svs": int(vps_id)})

    # Functions: Stop VM
    def stop_vm(self, vps_id: int) -> dict:
        """
        Stop a specific VM.
        :param vps_id: VPS ID number
        """
        return self.__request("GET", {"act": "stop", "svs": int(vps_id)})

    # Functions: List OS
    def list_os(self, vps_id: int) -> list:
        """
        List available OSes for a specific VM.
        :param vps_id: VPS ID number
        """
        req = self.__request("GET", {"act": "ostemplate", "svs": int(vps_id)})
        return req.get("oslist", {}).get("vzo", [])

    # Functions: Restart VM
    def restart_vm(self, vps_id: int) -> dict:
        """
        Restart a specific VM.
        :param vps_id: VPS ID number
        """
        return self.__request("GET", {"act": "restart", "svs": int(vps_id)})


    # Private functions: Request List VDF
    def __req_list_vdf(self, vps_id: int) -> dict:
        """
        HTTP Request of List VDFs for a specific VM.
        :param vps_id: VPS ID number
        """
        return self.__request("GET", {"act": "managevdf", "svs": int(vps_id)})

    # Functions: List VDF
    def list_vdf(self, vps_id: int) -> list:
        """
        List VDFs for a specific VM.
        :param vps_id: VPS ID number
        """
        req = self.__req_list_vdf(vps_id)
        return req.get("haproxydata", [])

    # Functions: Get VDF additional info
    def get_vdf_info(self, vps_id: int) -> dict:
        """
        Get VDF additional info.
        :param vps_id: VPS ID number
        """
        req = self.__req_list_vdf(vps_id)
        vpses = req.get("vpses", {})
        dest_ips = []
        if vpses:
            first_vps = next(iter(vpses.values()), {})
            dest_ips = list(first_vps.get("ips", {}).keys())
        return {
            "supported_protocols": req.get("supported_protocols", []),
            "src_ips": req.get("arr_haproxy_src_ips", []),
            "dest_ips": dest_ips
        }

    # Functions: Add VDF
    def add_vdf(
        self,
        vps_id: int,
        protocol: str,
        src_port: int,
        src_hostname: str,
        dest_ip: str,
        dest_port: int
    ) -> dict:
        """
        Add a VDF for a specific VM.
        :param vps_id: VPS ID number
        :param protocol: Domain Forwarding protocol
        :param src_port: Source port (if using HTTP/HTTPS protocol, use 80/443)
        :param src_hostname: Source domain, if using HTTP/HTTPS protocol
        :param dest_ip: Destination IP
        :param dest_port: Destination port (if using HTTP/HTTPS protocol, use 80/443)
        """
        req = self.__request(
            "POST",
            params_dict={"act": "managevdf"},
            data_dict={
                "svs": int(vps_id),
                "vdf_action": "addvdf",
                "protocol": protocol,
                "src_port": src_port,
                "src_hostname": src_hostname,
                "dest_ip": dest_ip,
                "dest_port": dest_port,
            },
        )
        if "error" in req:
            error_code = list(req["error"].keys())[0] if req["error"] else ""
            error_message = list(req["error"].values())[0] if req["error"] else ""
            return {
                "error": req["error"],
                "error_code": error_code,
                "error_message": error_message,
            }
        return req

    def delete_vdf(self, vps_id: int, vdf_id: int) -> dict:
        """
        Delete a VDF entry for a specific VM.
        :param vps_id: VPS ID number
        :param vdf_id: VDF ID number
        """
        return self.__request(
            "POST",
            params_dict={"act": "managevdf"},
            data_dict={
                "svs": int(vps_id),
                "vdf_action": "delvdf",
                "vdfid": int(vdf_id)
            },
        )

    def edit_vdf(self, vps_id: int, vdf_id: int, protocol: str, src_port: int, src_hostname: str, dest_ip: str, dest_port: int) -> dict:
        """
        Edit a VDF for a specific VM.
        :param vps_id: VPS ID number
        :param vdf_id: VDF ID number
        :param protocol: Domain Forwarding protocol
        :param src_port: Source port (if using HTTP/HTTPS protocol, use 80/443)
        :param src_hostname: Source domain, if using HTTP/HTTPS protocol
        :param dest_ip: Destination IP
        :param dest_port: Destination port (if using HTTP/HTTPS protocol, use 80/443)
        """
        return self.__request(
            "POST",
            params_dict={"act": "managevdf"},
            data_dict={
                "svs": int(vps_id),
                "vdf_action": "editvdf",
                "vdfid": int(vdf_id),
                "protocol": protocol,
                "src_port": src_port,
                "src_hostname": src_hostname,
                "dest_ip": dest_ip,
                "dest_port": dest_port,
            },
        )
