# Restart the prepared Windows workspace without installing system services.
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$localFolder = Join-Path $projectRoot '.local'
$pythonPath = Join-Path $projectRoot 'backend/.venv/Scripts/python.exe'
$postgresFolder = Join-Path $projectRoot '.tools/postgres'
$databaseFolder = Join-Path $localFolder 'postgres-data'
foreach ($requiredPath in @($pythonPath, $postgresFolder, $databaseFolder, (Join-Path $projectRoot 'backend/.env'), (Join-Path $projectRoot 'frontend/node_modules'))) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw 'This helper requires the prepared local Windows workspace. See README.md for a fresh setup.'
    }
}
function Test-LocalPort([int]$port) {
    $client = New-Object Net.Sockets.TcpClient
    try { return $client.ConnectAsync('127.0.0.1', $port).Wait(300) -and $client.Connected }
    catch { return $false }
    finally { $client.Dispose() }
}
# PostgreSQL portable binaries need ASCII paths on Windows.
$filesystem = New-Object -ComObject Scripting.FileSystemObject
$shortRoot = $filesystem.GetFolder($projectRoot).ShortPath
$shortPostgres = $filesystem.GetFolder($postgresFolder).ShortPath
if (-not (Test-LocalPort 5433)) {
    & "$shortPostgres/bin/pg_ctl.exe" -D "$shortRoot/.local/postgres-data" -l "$shortRoot/.local/postgres.log" -o '-h 127.0.0.1 -p 5433' -w start
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL did not start. Check .local/postgres.log.' }
}
if (-not (Test-LocalPort 8000)) {
    Start-Process -FilePath $pythonPath -ArgumentList @("$shortRoot/backend/manage.py", 'runserver', '127.0.0.1:8000', '--noreload') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $localFolder 'backend.log') -RedirectStandardError (Join-Path $localFolder 'backend-error.log') | Out-Null
}
if (-not (Test-LocalPort 5173)) {
    Get-Command npm.cmd -ErrorAction Stop | Out-Null
    Start-Process -FilePath $env:ComSpec -ArgumentList @('/d', '/c', 'npm.cmd run dev') -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $localFolder 'frontend.log') -RedirectStandardError (Join-Path $localFolder 'frontend-error.log') | Out-Null
}
Write-Host 'Local preview: http://127.0.0.1:5173'
Write-Host 'Django Admin: http://127.0.0.1:8000/admin/'
Write-Host 'Existing listeners are reused. Startup logs are in .local/.'
