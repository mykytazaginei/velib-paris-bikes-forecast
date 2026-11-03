Set-Location(Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force backups | Out-Null
$ErrorActionPreference = "Stop"
try{
    docker compose exec -T db pg_dump -U velib -d velib -Fc -f /tmp/velib.dump
    if ($LASTEXITCODE -ne 0) {throw "pg_dump failed"}
    $stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
    $path = "backups\velib_$stamp.dump"
    docker compose cp db:/tmp/velib.dump $path
    if ($LASTEXITCODE -ne 0) {throw "copy failed"}
    $size = (Get-Item $path).Length
    if ($size -eq 0) {throw "backup is empty"}
    docker compose exec -T db rm /tmp/velib.dump
    if ($LASTEXITCODE -ne 0) {throw "removing failed"}
    Get-ChildItem backups\*.dump | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-28)} | Remove-Item
    Add-Content -Path backups\backup.log -Value "$stamp OK $size bytes"
}
catch {
    $stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
    Add-Content -Path backups\backup.log -Value "$stamp FAILED: $_"
    Write-Host "Script failed: $_"
    exit 1
}