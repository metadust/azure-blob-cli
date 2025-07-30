import os
import sys
import logging
from azure.storage.blob import BlobServiceClient
from tqdm import tqdm
from datetime import datetime
from typing import List, Optional

ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME")
ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")

if not ACCOUNT_NAME or not ACCOUNT_KEY:
    print("! Please set the AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY environment variables.")
    sys.exit(1)

CONNECTION_STRING = (
    f"DefaultEndpointsProtocol=https;"
    f"AccountName={ACCOUNT_NAME};"
    f"AccountKey={ACCOUNT_KEY};"
    f"EndpointSuffix=core.windows.net"
)

blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)
def convert_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int((len(str(size_bytes)) - 1) // 3)
    p = 1024 ** i
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def list_containers() -> None:
    print("Containers:")
    for container in blob_service_client.list_containers():
        container_name = container.name
        container_client = blob_service_client.get_container_client(container_name)
        total_size = 0
        count = 0
        for blob in container_client.list_blobs():
            total_size += blob.size
            count += 1
        size_str = convert_size(total_size)
        print(f"• {container_name:30} | {count:5} files | {size_str}")

def list_files(container_name: str, prefix: Optional[str] = None) -> List[str]:
    container_client = blob_service_client.get_container_client(container_name)
    blobs = list(container_client.list_blobs(name_starts_with=prefix))
    
    if not blobs:
        print(f"No blobs found in '{container_name}' with prefix '{prefix or ''}'")
        return []

    print(f"\n Contents of '{container_name}':\n")
    for i, blob in enumerate(blobs):
        size_str = convert_size(blob.size)
        mod = blob.last_modified.strftime("%Y-%m-%d %H:%M")
        print(f"[{i:03}] {blob.name} | {size_str:10} | Last modified: {mod}")
    
    return [blob.name for blob in blobs]

def download_file(container_name: str, blob_name: str, dest_folder: Optional[str] = None, overwrite=False) -> None:
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    folder = dest_folder or container_name
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, os.path.basename(blob_name))

    if os.path.exists(file_path) and not overwrite:
        print(f" Skipping existing file: {file_path}")
        return

    with open(file_path, "wb") as f:
        data = blob_client.download_blob()
        total = data.size
        with tqdm.wrapattr(f, "write", total=total, desc=f"⬇ {blob_name}") as fout:
            fout.write(data.readall())
    
    print(f"Downloaded: {file_path}")

def download_container(container_name: str, prefix: Optional[str] = None, overwrite=False) -> None:
    blob_names = list_files(container_name, prefix)
    if not blob_names:
        return
    print(f"\n⬇ Downloading entire container: '{container_name}' ({len(blob_names)} files)")
    for blob_name in blob_names:
        download_file(container_name, blob_name, overwrite=overwrite)
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Azure Blob Storage Tool")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list_containers")

    list_files_cmd = subparsers.add_parser("list_files")
    list_files_cmd.add_argument("container_name")
    list_files_cmd.add_argument("--prefix", help="Filter files by prefix")

    download_file_cmd = subparsers.add_parser("download_file")
    download_file_cmd.add_argument("container_name")
    download_file_cmd.add_argument("file_name_or_index")
    download_file_cmd.add_argument("--prefix", help="Use index based on prefix filtering")
    download_file_cmd.add_argument("--overwrite", action="store_true")

    download_all_cmd = subparsers.add_parser("download_container")
    download_all_cmd.add_argument("container_name")
    download_all_cmd.add_argument("--prefix", help="Filter files by prefix")
    download_all_cmd.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()

    if args.command == "list_containers":
        list_containers()
    elif args.command == "list_files":
        list_files(args.container_name, prefix=args.prefix)
    elif args.command == "download_file":
        names = list_files(args.container_name, prefix=args.prefix)
        try:
            index = int(args.file_name_or_index)
            blob_name = names[index]
        except ValueError:
            blob_name = args.file_name_or_index
        download_file(args.container_name, blob_name, overwrite=args.overwrite)
    elif args.command == "download_container":
        download_container(args.container_name, prefix=args.prefix, overwrite=args.overwrite)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

