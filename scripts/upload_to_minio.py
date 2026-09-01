import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from storage_client import upload_file, is_available


def upload_directory(local_dir, prefix):
    if not os.path.isdir(local_dir):
        print(f"Skipping (not found): {local_dir}")
        return
    for root, _, files in os.walk(local_dir):
        for fname in files:
            local_path = os.path.join(root, fname)
            object_name = f"{prefix}/{fname}"
            url = upload_file(local_path, object_name)
            print(f"Uploaded {local_path} -> {url}")


if __name__ == "__main__":
    if not is_available():
        print("ERROR: MinIO server not reachable at http://localhost:9000")
        print("Start it first with: .\\start_minio.ps1  (in a separate terminal)")
        sys.exit(1)

    upload_directory("storage/fasta", "fasta")
    upload_directory("storage/jbrowse", "jbrowse")
    print("\nDone. View uploaded files at http://localhost:9001")