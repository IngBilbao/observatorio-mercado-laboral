<#
.SYNOPSIS
    Registra (o elimina) una tarea programada de Windows que ejecuta el pipeline
    Python del Observatorio cada N horas.

.DESCRIPTION
    Es el "componente real-time del data layer" de la arquitectura event-driven:
    Task Scheduler dispara el pipeline → Python procesa → CSVs en OneDrive →
    Power Automate detecta cambios y notifica.

.PARAMETER IntervaloHoras
    Cada cuántas horas se ejecuta. Por defecto: 6 (4 veces al día).

.PARAMETER NombreTarea
    Nombre de la tarea en Task Scheduler. Por defecto: BilbaoAnalytics_Observatorio.

.PARAMETER ConAdzuna
    Si se especifica, incluye ingesta + merge de Adzuna en cada corrida.

.PARAMETER Rapido
    Si se especifica, salta Prophet (paso más lento). Recomendado para corridas
    frecuentes.

.PARAMETER Eliminar
    Elimina la tarea programada en lugar de crearla.

.PARAMETER Estado
    Solo muestra el estado actual de la tarea sin modificarla.

.EXAMPLE
    .\programar_pipeline.ps1
    Crea tarea que corre cada 6 horas, sin Adzuna, sin --rapido.

.EXAMPLE
    .\programar_pipeline.ps1 -IntervaloHoras 4 -Rapido
    Cada 4 horas, saltando Prophet (más liviano).

.EXAMPLE
    .\programar_pipeline.ps1 -ConAdzuna -IntervaloHoras 24
    Pipeline completo con Adzuna, una vez al día.

.EXAMPLE
    .\programar_pipeline.ps1 -Estado
    Muestra estado y últimas ejecuciones.

.EXAMPLE
    .\programar_pipeline.ps1 -Eliminar
    Elimina la tarea programada.
#>
[CmdletBinding()]
param(
    [int]$IntervaloHoras = 6,
    [string]$NombreTarea = "BilbaoAnalytics_Observatorio",
    [switch]$ConAdzuna,
    [switch]$Rapido,
    [switch]$Eliminar,
    [switch]$Estado
)

$ErrorActionPreference = "Stop"

# ────────────────────────── Helpers de salida ──────────────────────────
function Write-Step($msg) { Write-Host "▶  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "✓  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "!  $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "✗  $msg" -ForegroundColor Red }
function Write-Title($msg) {
    Write-Host ""
    Write-Host ("═" * 68) -ForegroundColor DarkCyan
    Write-Host "  $msg" -ForegroundColor White
    Write-Host ("═" * 68) -ForegroundColor DarkCyan
}

# ────────────────────────── Estado actual ──────────────────────────
function Get-EstadoTarea {
    $tarea = Get-ScheduledTask -TaskName $NombreTarea -ErrorAction SilentlyContinue
    if ($null -eq $tarea) {
        Write-Warn "No existe ninguna tarea llamada '$NombreTarea'."
        return
    }
    $info = Get-ScheduledTaskInfo -TaskName $NombreTarea
    Write-Title "Estado de la tarea '$NombreTarea'"
    Write-Host "  Estado:                  $($tarea.State)"
    Write-Host "  Última ejecución:        $($info.LastRunTime)"
    Write-Host "  Último resultado:        0x$('{0:X}' -f $info.LastTaskResult)  $(if ($info.LastTaskResult -eq 0) {'(OK)'} else {'(error)'})"
    Write-Host "  Próxima ejecución:       $($info.NextRunTime)"
    Write-Host "  Número de ejecuciones:   $($info.NumberOfMissedRuns) perdidas"
    Write-Host ""
    Write-Host "  Acción:" -ForegroundColor Cyan
    $tarea.Actions | ForEach-Object {
        Write-Host "    $($_.Execute) $($_.Arguments)" -ForegroundColor Gray
    }
}

# ────────────────────────── Eliminar ──────────────────────────
function Remove-Tarea {
    $tarea = Get-ScheduledTask -TaskName $NombreTarea -ErrorAction SilentlyContinue
    if ($null -eq $tarea) {
        Write-Warn "No hay tarea '$NombreTarea' para eliminar."
        return
    }
    Unregister-ScheduledTask -TaskName $NombreTarea -Confirm:$false
    Write-Ok "Tarea '$NombreTarea' eliminada."
}

# ────────────────────────── Registrar ──────────────────────────
function Register-Tarea {
    $rutaProyecto  = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    $rutaPipeline  = Join-Path $rutaProyecto "python\99_pipeline.py"
    $rutaLogs      = Join-Path $rutaProyecto "logs"

    if (-not (Test-Path $rutaPipeline)) {
        Write-Err "No se encuentra: $rutaPipeline"
        exit 1
    }
    if (-not (Test-Path $rutaLogs)) {
        New-Item -ItemType Directory -Path $rutaLogs | Out-Null
    }

    # Localizar py launcher
    $pyExe = (Get-Command py.exe -ErrorAction SilentlyContinue).Path
    if ($null -eq $pyExe) {
        $pyExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Path
    }
    if ($null -eq $pyExe) {
        Write-Err "No se encontro Python en el PATH. Instalalo o agregalo al PATH."
        exit 1
    }

    # Construir argumentos del pipeline
    $argsPipeline = @("-3.12", "`"$rutaPipeline`"")
    if ($ConAdzuna) { $argsPipeline += "--con-adzuna" }
    if ($Rapido)    { $argsPipeline += "--rapido" }

    # Wrapper PowerShell que redirige output a log con timestamp
    $cmdWrapper = "& '$pyExe' $($argsPipeline -join ' ') *>> '$rutaLogs\pipeline_`$(Get-Date -Format yyyyMMdd).log'"

    Write-Title "Configuración"
    Write-Host "  Proyecto:        $rutaProyecto"
    Write-Host "  Python:          $pyExe"
    Write-Host "  Pipeline:        $rutaPipeline"
    Write-Host "  Intervalo:       cada $IntervaloHoras hora(s)"
    Write-Host "  Con Adzuna:      $ConAdzuna"
    Write-Host "  Rápido:          $Rapido"
    Write-Host "  Logs:            $rutaLogs\pipeline_YYYYMMDD.log"
    Write-Host ""

    # Trigger: cada N horas, indefinidamente
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) `
        -RepetitionInterval (New-TimeSpan -Hours $IntervaloHoras)

    # Action: invocar PowerShell con el wrapper
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"$cmdWrapper`"" `
        -WorkingDirectory $rutaProyecto

    # Settings: que se ejecute aunque el equipo este con bateria, retomar si falla
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable `
        -MultipleInstances IgnoreNew

    # Principal: cuenta actual, solo si el usuario esta logueado (no en background)
    $principal = New-ScheduledTaskPrincipal `
        -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
        -LogonType Interactive

    # Quitar tarea previa si existe (idempotente)
    if (Get-ScheduledTask -TaskName $NombreTarea -ErrorAction SilentlyContinue) {
        Write-Step "Eliminando tarea previa con mismo nombre..."
        Unregister-ScheduledTask -TaskName $NombreTarea -Confirm:$false
    }

    Write-Step "Registrando tarea programada..."
    Register-ScheduledTask `
        -TaskName $NombreTarea `
        -Description "Observatorio del Mercado Laboral · pipeline Python cada $IntervaloHoras h" `
        -Trigger $trigger `
        -Action $action `
        -Settings $settings `
        -Principal $principal | Out-Null

    Write-Ok "Tarea '$NombreTarea' registrada exitosamente."
    Write-Host ""
    Get-EstadoTarea
    Write-Host ""
    Write-Step "Tip: corre manualmente la primera ejecución con:"
    Write-Host "    Start-ScheduledTask -TaskName '$NombreTarea'" -ForegroundColor Gray
    Write-Host "    Get-Content `"$rutaLogs\pipeline_$(Get-Date -Format yyyyMMdd).log`" -Tail 30 -Wait" -ForegroundColor Gray
}

# ────────────────────────── Main ──────────────────────────
if ($Estado)        { Get-EstadoTarea; exit 0 }
if ($Eliminar)      { Remove-Tarea;    exit 0 }
Register-Tarea
