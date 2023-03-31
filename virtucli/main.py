from argparse import ArgumentParser
from appdirs import user_config_dir
from configparser import ConfigParser
from tabulate import tabulate
import json

from virtualizorapi import Api

def default_config_path():
    appname = "virtucli"
    path = user_config_dir(appname)
    return path

def init_args():
    parser = ArgumentParser(description="Basic management of Virtualizor VMs from CLI.")
    parser.add_argument("-c", "--config", help="Custom configuration file", required=False)

    # Subcommand
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    ## List VM
    listVM = subparsers.add_parser("listvm", help="List available VMs")

    ## VM info
    VMInfo = subparsers.add_parser("vminfo", help="Get specific VM info")
    VMInfo.add_argument("-i", "--id", help="VM UID", required=True)

    ## List VDF
    listVDF = subparsers.add_parser("listvdf", help="List available VMs")

    # Parse arguments
    args = parser.parse_args()
    return args

def main():
    args = init_args()

    config = ConfigParser()
    if args.config:
        config.read(args.config)
    else:
        config.read(default_config_path())

    # Setup API class
    serverURL = config["Server"]["SERVER_URL"]
    apiKey = config["Server"]["API_KEY"]
    apiPass = config["Server"]["API_PASS"]
    api = Api(serverURL, apiKey, apiPass)

    if args.command == "listvm":
        vms = api.listVM()["vs"]

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
    elif args.command == "vminfo":
        info = api.VMInfo(args.id)["info"]

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
