param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$UvicornArgs
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$python = if (Test-Path ".\.venv\Scripts\python.exe") {
    ".\.venv\Scripts\python.exe"
} else {
    "python"
}

$port = & $python -c "from api import config; print(config.API_PORT)"
& $python -m uvicorn api.main:app --port $port @UvicornArgs
exit $LASTEXITCODE
