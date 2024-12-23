RequestExecutionLevel admin

Section OutputPath
    SetOutPath $INSTDIR
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

SilentInstall silent
SilentUninstall silent

Section PythonInstall
    SetOutPath $INSTDIR\resources
    File "${BUILD_RESOURCES_DIR}\python_installer.exe"
    ExecWait '"$INSTDIR\resources\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0'
SectionEnd

Section ServiceInstall
    SetOutPath $INSTDIR\resources
    File "${BUILD_RESOURCES_DIR}\simple_service.py"
    File "${BUILD_RESOURCES_DIR}\install_service.bat"
    ExecWait '"$INSTDIR\resources\install_service.bat"'
SectionEnd

Section TaskSchedulerInstall
    SetOutPath $INSTDIR\resources
    File "${BUILD_RESOURCES_DIR}\simple_task.py"
    ExecWait 'schtasks /create /sc daily /mo 1 /tn "Simple Task" /tr "\"C:\\Program Files\\Python310\\python.exe\" \"$INSTDIR\resources\simple_task.py\"" /st 12:00 /ru SYSTEM /rl HIGHEST /f'
    ExecWait 'schtasks /run /tn "Simple Task"'
SectionEnd

Section "Uninstall"
    ; Stop the service
    ExecWait 'sc stop SimpleService'

    ; Wait for the service to stop
    Sleep 5000

    ; Delete the service
    ExecWait 'sc delete SimpleService'

    ; Wait for the service removal
    Sleep 5000

    ; Uninstall Python
    ExecWait '"C:\\Program Files\\Python310\\python.exe" -m pip uninstall -y requests'

    ; Delete the scheduled task
    ExecWait 'schtasks /delete /tn "Simple Task" /f'

    ; Wait for the task deletion
    Sleep 5000

    ; Remove the installation directory
    RMDir /r "$INSTDIR"
SectionEnd