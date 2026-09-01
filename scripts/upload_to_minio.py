import os
from storage_client import upload_file

def upload_directory(local_dir, prefix):
    for root, _, files in os.walk(local_dir):
        for fname in files:
            local_path = os.path.join(root, fname)
            object_name = f"{prefix}/{fname}"
            url = upload_file(local_path, object_name)
            print(f"Uploaded {local_path} -> {url}")

if __name__ == "__main__":
    upload_directory("storage/fasta", "fasta")
    upload_directory("storage/jbrowse", "jbrowse")