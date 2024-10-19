from argparse import ArgumentParser
from configparser import ConfigParser
from appdirs import user_config_dir

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
