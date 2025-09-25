import logging
from tabulate import tabulate

def getVMInfo(api, id_: int) -> None:
    """Print detailed info for a specific VM."""
    info = api.vm_info(id_)
    if info.get("error"):
        logging.error(" Error fetching VM information!")
        return
    info = info["info"]

    table_headers = ["Name", "Value"]
    info_table = []

    # UID
    uid = info.get("vpsid", "-")
    info_table.append(["ID", uid])

    # Hostname
    hostname = info.get("hostname", "-")
    info_table.append(["Hostname", hostname])

    # OS
    os_name = info.get("vps", {}).get("os_name", "-")
    info_table.append(["OS", os_name])

    # IPs
    ips = ", ".join(ip for ip in info.get("ip", []))
    info_table.append(["IP Address(es)", ips])

    # Virtualization
    virt = info.get("vps", {}).get("virt", "-")
    info_table.append(["Virtualization", virt])

    # RAM
    ram = info.get("vps", {}).get("ram", "-")
    info_table.append(["RAM", ram])

    # CPU Cores
    cores = info.get("vps", {}).get("cores", "-")
    info_table.append(["CPU Cores", cores])

    print(tabulate(info_table, headers=table_headers, tablefmt="grid"))
