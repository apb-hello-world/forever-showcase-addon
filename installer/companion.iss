#ifndef AppVersion
  #define AppVersion "0.6.0"
#endif
[Setup]
AppId={{4715C90C-47E4-43B5-A9C1-B9D1E66732F0}
AppName=Forever Showcase Companion
AppVersion={#AppVersion}
AppPublisher=Forever Showcase
AppPublisherURL=https://github.com/apb-hello-world/forever-showcase-addon
AppUpdatesURL=https://github.com/apb-hello-world/forever-showcase-addon/releases
DefaultDirName={localappdata}\Programs\Forever Showcase Companion
DefaultGroupName=Forever Showcase
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=ForeverShowcaseCompanion-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\ForeverShowcaseCompanion.exe
CloseApplications=yes
RestartApplications=no
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Files]
Source: "..\dist\ForeverShowcaseCompanion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Forever Showcase Companion"; Filename: "{app}\ForeverShowcaseCompanion.exe"
Name: "{autodesktop}\Forever Showcase Companion"; Filename: "{app}\ForeverShowcaseCompanion.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\ForeverShowcaseCompanion.exe"; Description: "Open Forever Showcase Companion"; Flags: nowait postinstall skipifsilent
