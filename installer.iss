[Setup]
AppName=NetMonitor by Python
AppVersion=1.0
DefaultDirName={pf}\NetMonitor
DefaultGroupName=NetMonitor
OutputBaseFilename=NetMonitorSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\monitor_internet.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\NetMonitor"; Filename: "{app}\main.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\main.exe"; Description: "Ejecutar NetMonitor"; Flags: nowait postinstall skipifsilent

