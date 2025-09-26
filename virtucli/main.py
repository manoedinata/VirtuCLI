from argparse import ArgumentParser
from configparser import ConfigParser
from appdirs import user_config_dir
import os
import sys
import logging

import random

from .api import Api
from . import functions

def default_config_path() -> str:
    appname = "virtucli"
    path = user_config_dir(appname)
    return path

def init_args() -> object:
    parser = ArgumentParser(prog="virtucli", description="Basic management of Virtualizor VMs from CLI.")
    parser.add_argument("-c", "--config", help="Custom configuration file", required=False)

    # Subcommand
    subparsers = parser.add_subparsers(dest="command", required=True)

    ## Default config path
    configPath = subparsers.add_parser("configpath", help="Show default config path")

    ## List VM
    listVM = subparsers.add_parser("listvm", help="List available VMs")

    ## VM info
    VMInfo = subparsers.add_parser("vminfo", help="Get specific VM info")
    VMInfo.add_argument("-i", "--id", help="VM UID", required=True)

    ## Domain Forwarding
    vdf = subparsers.add_parser("vdf", help="Domain Forwarding management")
    vdf.add_argument("-i", "--id", help="VM UID. Will use IP", required=True)
    vdfSubparser = vdf.add_subparsers(dest="vdf_command", required=True)

    ### Domain Forwarding: List
    vdfList = vdfSubparser.add_parser("list", help="List VDF entry")
    vdfList.add_argument("--filter", help="Filter VDF entry", required=False)

    ### Domain Forwarding: Add
    vdfAdd = vdfSubparser.add_parser("add", help="Add a new VDF entry")
    vdfAdd.add_argument("--proto", help="Protocol to be used", required=True)
    vdfAdd.add_argument("--src", help="Source IP/domain", required=True)
    vdfAdd.add_argument("--src-port", help="Source port", required=True)
    vdfAdd.add_argument("--dest", help="Destination IP", required=True)
    vdfAdd.add_argument("--dest-port", help="Destination port", required=True)

    ### Domain Forwarding: Edit
    vdfEdit = vdfSubparser.add_parser("edit", help="Edit an existing VDF entry")
    vdfEdit.add_argument("--vdf-id", help="VDF ID to be edited", required=True)
    vdfEdit.add_argument("--proto", help="Protocol to be used", required=True)
    vdfEdit.add_argument("--src", help="Source IP/domain", required=True)
    vdfEdit.add_argument("--src-port", help="Source port", required=True)
    vdfEdit.add_argument("--dest", help="Destination IP", required=True)
    vdfEdit.add_argument("--dest-port", help="Destination port", required=True)

    ### Domain Forwarding: Delete
    vdfList = vdfSubparser.add_parser("delete", help="Delete a VDF entry")
    vdfList.add_argument("--vdf-id", help="VDF ID to be deleted", required=True)

    ## Domain Forwarding: Setup 20 ports
    # natPorts = vdfSubparser.add_parser("natports", help="[NAT] Setup 20 port forwardings for basic use, automatically")
    # natPorts.add_argument("-p", "--ports", help="Base ports to be used. For example, if 27000 is specified, then the added ports will be 27000, 27001, 27002, until 27020. Random ports will be used if not specified.", type=int, required=False)
    # natPorts.add_argument("--ssh", help="Use the first port for SSH port.", action="store_true", required=False)

    # Parse arguments
    args = parser.parse_args()
    return args

def main() -> None:
    args = init_args()

    if args.command == "configpath":
        print(default_config_path())
        return

    # Pre-check: Abort if config file not found
    config_path = args.config if args.config else default_config_path() + "/config.ini"
    if not os.path.isfile(config_path):
        print(
            f"Error: Configuration file not found at '{config_path}'. " \
            "Please provide a valid config file or specify with '-c/--config'."
        )
        print(f"Or, place the config file at the default location: '{config_path}'")
        sys.exit(1)

    config = ConfigParser()
    config.read(config_path)

    # Setup API class
    serverURL = config["Server"]["SERVER_URL"]
    apiKey = config["Server"]["API_KEY"]
    apiPass = config["Server"]["API_PASS"]
    api = Api(serverURL, apiKey, apiPass)

    if args.command == "listvm":
        functions.list_vm(api)

    elif args.command == "vminfo":
        functions.vm_info(api, args.id)

    elif args.command == "vdf":
        if args.vdf_command == "add":
            functions.vdf.add_vdf(api, args.src, args.src_port, args.dest, args.dest_port)
        elif args.vdf_command == "list":
            functions.vdf.list_vdf(api, int(args.id), args.filter if args.filter else None)
        elif args.vdf_command == "edit":
            functions.vdf.edit_vdf(
                api, int(args.id), int(args.vdf_id),
                args.src, int(args.src_port), args.dest, int(args.dest_port), args.proto
            )
        elif args.vdf_command == "delete":
            functions.vdf.delete_vdf(api, int(args.id), int(args.vdf_id))

        # elif args.vdf_command == "natports":
        #     ports = args.ports
        #     if not ports:
        #         ports = random.randint(25001, 64000)
        #     length_of_ports = 20

        #     # Determine which IP to be used (random, shall we?)
        #     vdf_info = api.get_vdf_info(int(args.id))
        #     src_ips = random.choice(vdf_info["src_ips"]) if vdf_info["src_ips"] else None
        #     dest_ips = random.choice(vdf_info["dest_ips"]) if vdf_info["dest_ips"] else None

        #     if not src_ips or not dest_ips:
        #         print("Error: No available source or destination IPs.")
        #         sys.exit(1)

        #     # SSH
        #     if args.ssh:
        #         result = api.add_vdf(int(args.id), "TCP", ports, src_ips, dest_ips, 22)
        #         if "error" in result:
        #             print(f"SSH Port Error: {result.get('error_message', 'Unknown error')} ({result.get('error_code', '')})")
        #         ports += 1
        #         length_of_ports -= 1

        #     # Add ports
        #     for port in range(ports, ports + length_of_ports):
        #         result = api.add_vdf(int(args.id), "TCP", port, src_ips, dest_ips, port)
        #         if "error" in result:
        #             print(f"Port {port} Error: {result.get('error_message', 'Unknown error')} ({result.get('error_code', '')})")
