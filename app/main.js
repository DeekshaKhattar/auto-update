const { app, BrowserWindow, ipcMain, ipcRenderer } = require("electron");
// const MainScreen = require("./screens/main/mainScreen");
// const Globals = require("./globals");
const { autoUpdater } = require("electron-updater");
const path = require('path');
console.log('MainScreen path:', path.join(__dirname, './screens/main/mainScreen'));
const { exec, spawn } = require('child_process');
const fs = require('fs');
const pathToInstallServiceBat = 'D:\\autoupdate\\auto-update\\app\\build\\install_service.bat';

const MainScreen = require(path.join(__dirname, './screens/main/mainScreen'));
let curWindow;

//Basic flags
autoUpdater.autoDownload = false;
autoUpdater.autoInstallOnAppQuit = true;

function createWindow() {
  curWindow = new MainScreen();
}

// Function to copy system_health.py from build folder to resources folder
function copySystemHealthFile() {
  const sourcePath = path.join(__dirname, "build", "system_health.py");
  const destinationPath = "C:\\Program Files\\Autoupdater app\\resources\\system_health.py";

  console.log("Source Path:", sourcePath);
  console.log("Destination Path:", destinationPath);

  const scriptContent = `
    $sourcePath = "${sourcePath}"
    $destinationPath = "${destinationPath}"
    if (!(Test-Path -Path $sourcePath)) {
      Write-Error "Source file not found: $sourcePath"
      exit 1
    }
    $destinationDir = Split-Path -Parent $destinationPath
    if (!(Test-Path -Path $destinationDir)) {
      New-Item -ItemType Directory -Path $destinationDir -Force
    }
    Start-Process -FilePath "powershell.exe" -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', "Copy-Item -Path '$sourcePath' -Destination '$destinationPath' -Force" -Verb RunAs
  `;

  const tempScriptPath = path.join(__dirname, "copy_script.ps1");
  fs.writeFileSync(tempScriptPath, scriptContent);

  const command = `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${tempScriptPath}"`;

  exec(command, (err, stdout, stderr) => {
    if (err) {
      console.error("Error during file copy:", err);
      return;
    }
    console.log(stdout);
    if (stderr) {
      console.error(stderr);
    }
    fs.unlinkSync(tempScriptPath); // Clean up the temporary script file
  });
}

/*Download Completion Message*/
app.whenReady().then(() => {
  createWindow();
  // copySystemHealthFile();
  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length == 0) createWindow();
  });

  autoUpdater.checkForUpdates();
  console.log(`Checking for updates. Current version: ${app.getVersion()}`);

  curWindow.showMessage(`Checking for updates. Current version ${app.getVersion()}`);

  // Ensure elevated permissions and run the batch file to install the service
  // runBatchWithElevatedPermissions(pathToInstallServiceBat);

  curWindow.showMessage(`Update downloaded. Current version ${app.getVersion()}`);
});


/*New Update Available*/
autoUpdater.on("update-available", (info) => {
  curWindow.showMessage(`Update available. Current version ${app.getVersion()}`);
  let pth = autoUpdater.downloadUpdate();
  curWindow.showMessage(pth);
});

autoUpdater.on("update-not-available", (info) => {
  curWindow.showMessage(`No update available. Current version ${app.getVersion()}`);
});



/*Download Completion Message*/
autoUpdater.on("update-downloaded", (info) => {
  exec(pathToInstallServiceBat, (err, stdout, stderr) => {
    if (err) {
      console.error('Error reinstalling service:', err);
      return;
    }
    const pythonPaths = [
      'C:\\Program Files\\Python312\\python.exe',
      'C:\\Program Files\\Python310\\python.exe'
    ];
  
    const scriptPath = `"${app.getAppPath()}\\resources\\system_health.py"`;
  
    const tasks = [
      "Demo 1.1",
      "Demo 2.1",
      "Demo 1.2",
      "Demo 2.2"
    ];
  
    // Remove existing tasks
    tasks.forEach((taskName) => {
      const deleteCommand = `schtasks /delete /tn "${taskName}" /f`;
      exec(deleteCommand, (err, stdout, stderr) => {
        if (err) {
          console.error(`Error deleting task ${taskName}:`, err);
          return;
        }
        console.log(`Task ${taskName} deleted successfully`);
      });
    }); 
  
    // Create new tasks
    setTimeout(() => {
      tasks.forEach((taskName, index) => {
        const pythonPath = pythonPaths[index % pythonPaths.length];
        const time = index < 2 ? "14:00" : "18:00"; // First two tasks at 14:00, next two at 18:00
  
        const createCommand = `schtasks /create /sc daily /mo 1 /tn "${taskName}" /tr "${pythonPath} ${scriptPath}" /st ${time} /ru SYSTEM /rl HIGHEST /f`;
        exec(createCommand, (err, stdout, stderr) => {
          if (err) {
            console.error(`Error creating task ${taskName}:`, err);
            return;
          }
          console.log(`Task ${taskName} created successfully`);
          console.log('stdout:', stdout);
          console.log('stderr:', stderr);
        });
      });
    }, 2000);

      // Copy system_health.py from build folder to resources folder

  copySystemHealthFile();
  });
  curWindow.showMessage(`Update downloaded. Current version ${app.getVersion()}`);
  
});

autoUpdater.on("error", (info) => {
  curWindow.showMessage(info);
});

//Global exception handler
process.on("uncaughtException", function (err) {
  console.log(err);
});

app.on("window-all-closed", function () {
  if (process.platform != "darwin") app.quit();
});


