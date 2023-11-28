if ([Environment]::Is64BitOperatingSystem -eq "True") {
    #Write-Host "64-bit OS"
    $PF=${env:ProgramFiles(x86)}
}
else {
    #Write-Host "32-bit OS"
    $PF=$env:ProgramFiles
}

if ($(Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") -eq "true") {
    # 结束进程
    taskkill /im chrome.exe /f
    taskkill /im GoogleUpdate.exe /f
    # Google Chrome 更新服务 (sysin)
    #这里也可以使用 sc.exe stop "service name"
    Stop-Service -Name "gupdate"
    Stop-Service -Name "gupdatem"
    Stop-Service -Name "GoogleChromeElevationService"
    # Windows 10 默认 PS 版本 5.1 没有 Remove-Service 命令
    # This cmdlet was added in PS v6. See https://docs.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-powershell-core-60?view=powershell-6#cmdlet-updates.
    #Remove-Service -Name "gupdate"
    #Remove-Service -Name "gupdatem"
    #Remove-Service -Name "GoogleChromeElevationService"
    # sc 在 PowerShell 中是 Set-Content 别名，所以要使用 sc.exe 否则执行后无任何效果
    sc.exe delete "gupdate"
    sc.exe delete "gupdatem"
    sc.exe delete "GoogleChromeElevationService"
    # 任务计划企业版
    #schtasks.exe /Delete /TN \GoogleUpdateBrowserReplacementTask /F
    #schtasks.exe /Delete /TN \GoogleUpdateTaskMachineCore /F
    #schtasks.exe /Delete /TN \GoogleUpdateTaskMachineUA /F
    Get-ScheduledTask -taskname GoogleUpdate* | Unregister-ScheduledTask -Confirm: $false
    # 移除更新程序
    Remove-Item "$PF\Google\Update\" -Recurse -Force
    Write-Output "Disable Google Chrome Enterprise x64 Auto Update Successful!"
}
elseif ($(Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe") -eq "true") {
    # 结束进程
    taskkill /im chrome.exe /f
    taskkill /im GoogleUpdate.exe /f
    # 删除 Google Chrome 更新服务
    #这里也可以使用 sc.exe stop "service name"
    Stop-Service -Name "gupdate"
    Stop-Service -Name "gupdatem"
    Stop-Service -Name "GoogleChromeElevationService"
    # Windows 10 默认 PS 版本 5.1 没有 Remove-Service 命令，糟糕！
    # This cmdlet was added in PS v6. See https://docs.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-powershell-core-60?view=powershell-6#cmdlet-updates.
    #Remove-Service -Name "gupdate"
    #Remove-Service -Name "gupdatem"
    #Remove-Service -Name "GoogleChromeElevationService"
    # sc 在 PowerShell 中是 Set-Content 别名，所以要使用 sc.exe 否则执行后无任何效果
    sc.exe delete "gupdate"
    sc.exe delete "gupdatem"
    sc.exe delete "GoogleChromeElevationService"
    # 删除任务计划
    #schtasks.exe /Delete /TN \GoogleUpdateBrowserReplacementTask /F
    #schtasks.exe /Delete /TN \GoogleUpdateTaskMachineCore /F
    #schtasks.exe /Delete /TN \GoogleUpdateTaskMachineUA /F
    Get-ScheduledTask -taskname GoogleUpdate* | Unregister-ScheduledTask -Confirm: $false
    # 移除更新程序
    Remove-Item "$PF\Google\Update\" -Recurse -Force
    Write-Output "Disable Google Chrome Enterprise x86 Auto Update Successful!"
}
else {
    Write-Output "No Google Chrome Enterprise Installation Detected!"
}