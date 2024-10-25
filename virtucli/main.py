from argparse import ArgumentParser
from configparser import ConfigParser
from appdirs import user_config_dir

import random
from virtualizorapi import Api

from .utils import listVM
from .utils import getVMInfo

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

    ## Domain Forwarding: Setup 20 ports
    natPorts = subparsers.add_parser("natports", help="[NAT] Setup 20 port forwardings for basic use, automatically")
    natPorts.add_argument("-i", "--id", help="VM UID", required=True)
    natPorts.add_argument("-p", "--ports", help="Base ports to be used. For example, if 27000 is specified, then the added ports will be 27000, 27001, 27002, until 27020. Random ports will be used if not specified.", type=int, required=False)
    natPorts.add_argument("--ssh", help="Use the first port for SSH port.", action="store_true", required=False)

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
        listVM(api)

    elif args.command == "vminfo":
        getVMInfo(api, args.id)

    elif args.command == "natports":
        ports = args.ports
        if not ports: ports = random.randint(25001, 64000)
        lengthOfPorts = 20

        # Determine which IP to be used (random, shall we?)
        vdfInfo = api.getVDFInfo(args.id)
        src_ips = random.choice(vdfInfo["src_ips"])
        dest_ips = random.choice(vdfInfo["dest_ips"])

        # SSH
        if args.ssh:
            api.addVDF(args.id, "TCP", port, src_ips, dest_ips, 22)
            ports += 1
            lengthOfPorts -= 1

        # Add ports
        for port in range(ports, ports + lengthOfPorts):
            api.addVDF(args.id, "TCP", port, src_ips, dest_ips, port)
