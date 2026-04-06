Get-Command opencode -ErrorAction SilentlyContinue | Select-Object Source
if (-not $?) { Write-Host "opencode not in PATH" }
