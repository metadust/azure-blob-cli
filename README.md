# Azure Blob CLI Tool

A command-line tool to interact with Azure Blob Storage. Easily list containers, view file contents, and download files or entire containers.

##  Features

- List all containers
- List files in a container with optional prefix filtering
- Download individual files by name or index
- Download all files from a container

##  Setup

### 1. Clone the repo

```bash
git clone https://github.com/metadust/azure-blob-cli.git
cd azure-blob-cli
```

### 2. Create a `.env` file

```env
# .env
AZURE_ACCOUNT_NAME=your_account_name
AZURE_ACCOUNT_KEY=your_account_key
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 🛠 Usage

```bash
python azure_blob_cli.py [command] [options]
```

### Commands

```text
list_containers
    Lists all available containers.

list_files <container_name> [--prefix=PREFIX]
    Lists files in a container (optionally filter by prefix).

download_file <container_name> <blob_name_or_index> [--prefix=PREFIX] [--overwrite]
    Downloads a specific file by name or index.

download_container <container_name> [--prefix=PREFIX] [--overwrite]
    Downloads all blobs in a container.
```

### Examples

```bash
# List all containers
python azure_blob_cli.py list_containers

# List all files in a container
python azure_blob_cli.py list_files my-container

# List files with a prefix filter
python azure_blob_cli.py list_files my-container --prefix=data/

# Download a file by index (with optional prefix filtering)
python azure_blob_cli.py download_file my-container 0 --prefix=logs/

# Download a specific file by name
python azure_blob_cli.py download_file my-container example.txt

# Download entire container contents (with overwrite enabled)
python azure_blob_cli.py download_container my-container --overwrite
```

## Tested With

- Python 3.8+
- Azure SDK for Python
- tqdm
