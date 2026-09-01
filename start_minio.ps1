# start_minio.ps1
# Launches MinIO as a standalone local object storage server.
# No Docker or admin rights required.

$env:MINIO_ROOT_USER = "minioadmin"
$env:MINIO_ROOT_PASSWORD = "minioadmin123"

$dataDir = Join-Path $PSScriptRoot "minio_data"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
}

Write-Host "Starting MinIO server..."
Write-Host "  API:    http://localhost:9000"
Write-Host "  Console: http://localhost:9001"
Write-Host "  Login:   minioadmin / minioadmin123"
Write-Host ""

& "$PSScriptRoot\minio.exe" server $dataDir --console-address ":9001"