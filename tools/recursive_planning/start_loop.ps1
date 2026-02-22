param(
    [string]$Workspace,
    [int]$SleepSeconds = 3600,
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

if (-not $Workspace) {
    $Workspace = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
} else {
    $Workspace = (Resolve-Path $Workspace).Path
}

$TriggerScript = Join-Path $Workspace "tools\recursive_planning\planning_trigger.py"
$WorkflowScript = Join-Path $Workspace "tools\recursive_planning\planning_workflow.py"
$ArtifactsDir = Join-Path $Workspace "artifacts\planning"
$LogFile = Join-Path $ArtifactsDir "recursive-loop.log"

New-Item -ItemType Directory -Force -Path $ArtifactsDir | Out-Null

function Write-LoopLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Content -Path $LogFile -Value "[$stamp] $Message"
}

Write-LoopLog "Loop worker started (workspace=$Workspace, sleep=${SleepSeconds}s, python=$PythonExe)"

while ($true) {
    try {
        $checkOutput = & $PythonExe $TriggerScript --check --workspace $Workspace 2>&1 | Out-String
        Write-LoopLog "Check output:`n$checkOutput"

        if ($checkOutput -match "Auto-trigger should activate: True") {
            $autoOutput = & $PythonExe $TriggerScript --auto --workspace $Workspace 2>&1 | Out-String
            Write-LoopLog "Auto trigger output:`n$autoOutput"

            $cycleOutput = & $PythonExe $WorkflowScript --full-cycle --workspace $Workspace 2>&1 | Out-String
            Write-LoopLog "Workflow output:`n$cycleOutput"
        } else {
            Write-LoopLog "No trigger condition met this cycle."
        }
    } catch {
        Write-LoopLog "Loop error: $($_.Exception.Message)"
    }

    Start-Sleep -Seconds $SleepSeconds
}
