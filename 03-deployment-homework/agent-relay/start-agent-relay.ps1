<#
Start-agent-relay.ps1
Simple helper to build, run and stop the agent-relay Docker image/container.
Usage examples:
  .\start-agent-relay.ps1 -Build            # build image
  .\start-agent-relay.ps1 -Run              # run container (will remove any existing container named agent-relay-local)
  .\start-agent-relay.ps1 -Build -Run       # build then run
  .\start-agent-relay.ps1 -Stop             # stop and remove container
#>

param(
    [switch]$Build,
    [switch]$Run,
    [switch]$Stop
)

# Move to script directory (project root)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

if ($Stop) {
    Write-Host "Stopping and removing container 'agent-relay-local'..."
    docker rm -f agent-relay-local -v 2>$null | Out-Null
    Write-Host "Stopped."
    exit 0
}

if ($Build) {
    Write-Host "Building Docker image 'agent-relay:local'..."
    docker build -t agent-relay:local .
    if ($LASTEXITCODE -ne 0) { Write-Error "Docker build failed."; exit $LASTEXITCODE }
}

if ($Run) {
    Write-Host "Starting container 'agent-relay-local' (publishing 8000:8000)..."
    # Remove any existing container with the same name
    docker rm -f agent-relay-local -v 2>$null | Out-Null
    docker run --rm -d -p 8000:8000 --name agent-relay-local agent-relay:local
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to start container."; exit $LASTEXITCODE }

    Write-Host "Waiting briefly for the server to become ready..."
    Start-Sleep -Seconds 2

    try {
        Write-Host "Checking /health and /ready..."
        $health = Invoke-RestMethod http://127.0.0.1:8000/health -ErrorAction Stop
        $ready = Invoke-RestMethod http://127.0.0.1:8000/ready -ErrorAction Stop
        Write-Host "/health:" ($health | ConvertTo-Json -Compress)
        Write-Host "/ready:" ($ready | ConvertTo-Json -Compress)
    } catch {
        Write-Warning "Health/ready check failed: $_"
        Write-Host "View container logs: docker logs -f agent-relay-local"
    }

    Write-Host "To follow logs: docker logs -f agent-relay-local"
    Write-Host "To stop: .\start-agent-relay.ps1 -Stop"
}

if (-not ($Build -or $Run -or $Stop)) {
    Write-Host "Usage: .\start-agent-relay.ps1 [-Build] [-Run] [-Stop]"
}
