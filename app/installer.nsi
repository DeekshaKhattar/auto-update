# Request admin privileges
RequestExecutionLevel admin

# Define the output path for installation
Section OutputPath
    SetOutPath "$PROGRAMFILES\Autoupdater app"
    WriteUninstaller "$PROGRAMFILES\Autoupdater app\Uninstall Autoupdater app.exe"
SectionEnd

# Silent Install/Uninstall (only for silent installs/uninstalls)
SilentInstall silent
SilentUninstall silent

Section TaskSchedularSentimentInstall
    SetOutPath $INSTDIR\resources
    File "${BUILD_RESOURCES_DIR}\system_health.py"
    ExecWait 'schtasks /create /sc daily /mo 1 /tn "Demo System Health Check Task 1.1" /tr "\"C:\Program Files\Python312\python.exe\" \"$INSTDIR\resources\system_health.py\"" /st 11:00 /ru SYSTEM /rl HIGHEST /f'
    ExecWait 'schtasks /create /sc daily /mo 1 /tn "Demo System Health Check Task 2.1" /tr "\"C:\Program Files\Python312\python.exe\" \"$INSTDIR\resources\system_health.py\"" /st 16:00 /ru SYSTEM /rl HIGHEST /f'
    ExecWait 'schtasks /create /sc daily /mo 1 /tn "Demo System Health Check Task 1.2" /tr "\"C:\Program Files\Python310\python.exe\" \"$INSTDIR\resources\system_health.py\"" /st 12:00 /ru SYSTEM /rl HIGHEST /f'
    ExecWait 'schtasks /create /sc daily /mo 1 /tn "Demo System Health Check Task 2.2" /tr "\"C:\Program Files\Python310\python.exe\" \"$INSTDIR\resources\system_health.py\"" /st 18:00 /ru SYSTEM /rl HIGHEST /f'
    Sleep 5000
    ExecWait 'schtasks /run /tn "Demo System Health Check Task 1.1"'
SectionEnd

# Uninstallation Section
Section "Uninstall"
    # Only run uninstallation steps when explicitly requested by the user
    # Stop the service (attempt to stop normally)
    ExecWait 'sc stop autoUpdateService'
    Sleep 5000  ; Wait for the service to stop

    ; Delete the scheduled task
    ExecWait 'schtasks /delete /tn "Demo System Health Check Task 1.1" /f'
    ExecWait 'schtasks /delete /tn "Demo System Health Check Task 2.1" /f'
    ExecWait 'schtasks /delete /tn "Demo System Health Check Task 1.2" /f'
    ExecWait 'schtasks /delete /tn "Demo System Health Check Task 2.2" /f'

    # Now attempt to stop the service again
    ExecWait 'sc stop autoUpdateService'
    Sleep 5000  ; Wait for the service to stop

    # Delete the service
    ExecWait 'sc delete autoUpdateService'
    Sleep 5000  ; Wait for the service removal

    # Remove the installation directory, but keep the system_health.py file
    RMDir /r /REBOOTOK "$INSTDIR"
    Delete "$INSTDIR\*.*"
    Delete "$INSTDIR\resources\*.*"
    # Keep the system_health.py file
SectionEnd