import logging
from tabulate import tabulate

from virtucli.api import Api

def list_vdf(api: Api, vps_id: int, filter_output: str = None) -> None:
    vdf = api.list_vdf(vps_id)
    if vdf.get("error"):
        logging.error(" Error fetching VDF information!")
        return

    table_headers = ["VDF ID", "Protocol", "Source", "Destination"]
    vdf_table = []
    for _, df in vdf.items():
        proto = df.get("protocol")
        if filter_output and proto.lower() != filter_output.lower():
            continue
        vdf_id = df.get("id")
        src_ip = df.get("src_hostname")
        src_port = df.get("src_port")
        dest_ip = df.get("dest_ip")
        dest_port = df.get("dest_port")
        vdf_table.append([
            vdf_id,
            proto,
            f"{src_ip}:{src_port}",
            f"{dest_ip}:{dest_port}"
        ])

    print(f"Total entries: {len(vdf_table)}")
    print(tabulate(vdf_table, headers=table_headers, tablefmt="grid"))

def add_vdf(api: Api, src_ip: str, src_port: int, dest_ip: str, dest_port: int, proto: str):
    src_port = int(src_port)
    dest_port = int(dest_port)

    result = api.add_vdf(
        int(id),
        proto,
        src_port,
        src_ip,
        dest_ip,
        dest_port
    )
    if "error" in result:
        logging.error(f" Error: {result.get('error_message', 'Unknown error')} ({result.get('error_code', '')})")
    else:
        print(f"Success adding port {src_port} --> {dest_port}!")
        print(tabulate([[
            proto,
            f"{src_ip}:{src_port}",
            f"{dest_ip}:{dest_port}"
        ]], headers=["Protocol", "Source", "Destination"], tablefmt="grid"))

def edit_vdf(api: Api, vps_id: int, vdf_id: int, src_ip: str = None, src_port: int = None, dest_ip: str = None, dest_port: int = None, proto: str = None) -> None:
    result = api.edit_vdf(vps_id, vdf_id, proto, src_port, src_ip, dest_ip, dest_port)
    if "error" in result:
        logging.error(f" Error: {result.get('error_message', 'Unknown error')} ({result.get('error_code', '')})")
    else:
        print(f"Success editing VDF ID {vdf_id}!")
        print(tabulate([[
            proto,
            f"{src_ip}:{src_port}",
            f"{dest_ip}:{dest_port}"
        ]], headers=["Protocol", "Source", "Destination"], tablefmt="grid"))
    return

def delete_vdf(api: Api, vps_id: int, vdf_id: int) -> None:
    result = api.delete_vdf(vps_id, vdf_id)
    if "error" in result:
        logging.error(f" Error: {result.get('error_message', 'Unknown error')} ({result.get('error_code', '')})")
    else:
        print(f"Success deleting VDF ID {vdf_id}!")
