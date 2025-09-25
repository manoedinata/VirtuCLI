import logging
from tabulate import tabulate

def listVM(api) -> None:
    """Print a table of all VMs."""
    vms = api.list_vm()
    if vms.get("error"):
        logging.error(" Error fetching VM information!")
        return
    vms = vms["vs"]

    table_headers = ["UID", "Hostname", "OS", "IP Addresses"]
    vm_table = []
    for uid, vm in vms.items():
        hostname = vm.get("hostname", "-")
        os_name = vm.get("os_name", "-")
        ips = ", ".join(ip for ip in vm.get("ips", {}).values())
        vm_table.append([uid, hostname, os_name, ips])

    print(tabulate(vm_table, headers=table_headers, tablefmt="grid"))