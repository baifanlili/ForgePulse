$ErrorActionPreference = "Stop"
Write-Host "Enabling WSL and Virtual Machine Platform..."
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:HypervisorPlatform /all /norestart
bcdedit /set hypervisorlaunchtype auto
Write-Host "Done. Please restart Windows, then open Docker Desktop again."
Read-Host "Press Enter to close"
