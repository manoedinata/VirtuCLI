from tabulate import tabulate

def listVM(api):
    vms = api.listVM()

    tableHeaders = ["UID", "Hostname", "OS", "IP Addresses"]
    vmTable= []
    for vm in vms:
        vmData = []
        vmData.append(vm)
        vmData.append(vms[vm]["hostname"])
        vmData.append(vms[vm]["os_name"])
        vmData.append(", ".join(ip for ip in vms[vm]["ips"].values()))
        vmTable.append(vmData)

    print(tabulate(vmTable, headers=tableHeaders, tablefmt="grid"))

def getVMInfo(api, id):
    info = api.VMInfo(id)

    tableHeaders = ["Name", "Value"]
    infoTable = []

    # Hostname
    hostnameTable = ["Hostname"]
    hostnameTable.append(info["hostname"])
    infoTable.append(hostnameTable)

    # OS
    osTable = ["OS"]
    osTable.append(info["vps"]["os_name"])
    infoTable.append(osTable)

    # IPs
    IPTable = ["IP Address(es)"]
    IPTable.append(", ".join(ip for ip in info["ip"]))
    infoTable.append(IPTable)

    # Virtualization
    virtTable = ["Virtualization"]
    virtTable.append(info["vps"]["virt"])
    infoTable.append(virtTable)

    # RAM
    RAMTable = ["RAM"]
    RAMTable.append(info["vps"]["ram"])
    infoTable.append(RAMTable)

    # CPU Cores
    coresTable = ["CPU Cores"]
    coresTable.append(info["vps"]["cores"])
    infoTable.append(coresTable)

    print(tabulate(infoTable, headers=tableHeaders, tablefmt="grid"))
