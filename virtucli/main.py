from argparse import ArgumentParser
from configparser import ConfigParser
from appdirs import user_config_dir
import os
import sys

import random
from virtualizorenduser import Api

from .utils import listVM
from .utils import getVMInfo

def default_config_path():
    appname = "virtucli"
    path = user_config_dir(appname)
    return path

def init_args():
    parser = ArgumentParser(prog="virtucli", description="Basic management of Virtualizor VMs from CLI.")
    parser.add_argument("-c", "--config", help="Custom configuration file", required=False)

    # Subcommand
    subparsers = parser.add_subparsers(dest="command", required=True)

    ## List VM
    listVM = subparsers.add_parser("listvm", help="List available VMs")

    ## VM info
    VMInfo = subparsers.add_parser("vminfo", help="Get specific VM info")
    VMInfo.add_argument("-i", "--id", help="VM UID", required=True)

    ## Domain Forwarding
    vdf = subparsers.add_parser("vdf", help="Domain Forwarding management")
    vdf.add_argument("-i", "--id", help="VM UID. Will use IP", required=True)
    vdfSubparser = vdf.add_subparsers(dest="vdf_command", required=True)

    ### Domain Forwarding: Add
    vdfAdd = vdfSubparser.add_parser("add", help="Add a new VDF entry")
    vdfAdd.add_argument("--proto", help="Protocol to be used", required=True)
    vdfAdd.add_argument("--src", help="Source IP/domain", required=True)
    vdfAdd.add_argument("--src-port", help="Source port", required=True)
    vdfAdd.add_argument("--dest", help="Destination IP", required=True)
    vdfAdd.add_argument("--dest-port", help="Destination port", required=True)

    ## Domain Forwarding: Setup 20 ports
    natPorts = vdfSubparser.add_parser("natports", help="[NAT] Setup 20 port forwardings for basic use, automatically")
    natPorts.add_argument("-p", "--ports", help="Base ports to be used. For example, if 27000 is specified, then the added ports will be 27000, 27001, 27002, until 27020. Random ports will be used if not specified.", type=int, required=False)
    natPorts.add_argument("--ssh", help="Use the first port for SSH port.", action="store_true", required=False)

    # Parse arguments
    args = parser.parse_args()
    return args

def main():
    args = init_args()

    # Pre-check: Abort if config file not found
    config_path = args.config if args.config else default_config_path() + "/config.ini"
    if not os.path.isfile(config_path):
        print(f"Error: Configuration file not found at '{config_path}'. Please provide a valid config file.")
        sys.exit(1)

    config = ConfigParser()
    config.read(config_path)

    # Setup API class
    serverURL = config["Server"]["SERVER_URL"]
    apiKey = config["Server"]["API_KEY"]
    apiPass = config["Server"]["API_PASS"]
    api = Api(serverURL, apiKey, apiPass)

    if args.command == "listvm":
        listVM(api)

    elif args.command == "vminfo":
        getVMInfo(api, args.id)

    elif args.command == "vdf":
        if args.vdf_command == "add":
            api.addVDF(
                args.id,
                args.proto,
                args.src_port,
                args.src,
                args.dest,
                args.dest_port
            )
            if api.error:
                print(f"Error: {api.error_message} ({api.error_code})")
            else:
                print("Success!")

        elif args.vdf_command == "natports":
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
