$TaskName = "KnowledgeBaseUpdater"
$PythonPath = (Get-Command python).Source
$ScriptPath = Join-Path $PSScriptRoot "update_index.py"
$WorkingDir = $PSScriptRoot
$LogFile = Join-Path $WorkingDir "logs\task_execution.log"

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDir

$Trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartInterval (New-TimeSpan -Minutes 30) `
    -RestartCount 3 `
    -StartWhenAvailable

$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Автоматическое ежедневное обновление FAISS базы знаний"

Write-Host "Задача '$TaskName' создана" -ForegroundColor Green
Write-Host "Запуск: каждый день в 6:00" -ForegroundColor Cyan
Write-Host "При ошибке: повтор каждые 30 мин (макс 3 раза)" -ForegroundColor Cyan