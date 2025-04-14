#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Installationspaket-Builder

Dieses Skript erstellt ein ausführbares Installationspaket für Windows.
"""
import os
import sys
import shutil
import platform
import subprocess
import argparse
from cx_Freeze import setup, Executable

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="VMware vSphere Reporter - Installationspaket-Builder")
    parser.add_argument('--outdir', default='build', help='Ausgabeverzeichnis für das Installationspaket')
    parser.add_argument('--version', default='1.0.0', help='Versionsnummer des Installationspakets')
    args = parser.parse_args()
    
    print("VMware vSphere Reporter - Installationspaket-Builder")
    print("===================================================")
    
    # Prüfe, ob wir auf Windows sind
    if platform.system() != "Windows":
        print("Warnung: Die Erstellung von Windows-Installationspaketen funktioniert am besten auf Windows.")
        print("Fortfahren auf eigene Gefahr...")
    
    # Erstelle temporäres Verzeichnis für Build-Dateien
    if os.path.exists("build"):
        print("Lösche vorhandenes Build-Verzeichnis...")
        shutil.rmtree("build")
    os.makedirs("build", exist_ok=True)
    
    # Kopiere benötigte Dateien in das Build-Verzeichnis
    print("Kopiere Programmdateien...")
    shutil.copy("installer_gui.py", "build/")
    
    # Suche nach Logo und anderen Assets
    print("Suche nach Assets...")
    if os.path.exists("images/logo_bechtle.png"):
        os.makedirs("build/images", exist_ok=True)
        shutil.copy("images/logo_bechtle.png", "build/images/")
    elif os.path.exists("attached_assets/logo_bechtle.png"):
        os.makedirs("build/images", exist_ok=True)
        shutil.copy("attached_assets/logo_bechtle.png", "build/images/")
    else:
        print("Warnung: Bechtle-Logo nicht gefunden!")
    
    # Generiere Windows-EXE mit cx_Freeze
    print("Erstelle ausführbares Installationspaket...")
    build_exe_options = {
        "packages": ["os", "sys", "PyQt5", "subprocess", "threading", "logging"],
        "excludes": ["tkinter", "unittest", "email", "http", "xml", "pydoc"],
        "include_files": [
            ("build/images", "images"),
        ],
        "include_msvcr": True,
    }
    
    # Optionales Paket für Windows-Verknüpfungen
    try:
        import win32com
        print("win32com gefunden - Verknüpfungen werden unterstützt")
    except ImportError:
        print("Warnung: win32com nicht gefunden - Installation von pywin32 empfohlen für Windows-Verknüpfungen")
    
    base = None
    if platform.system() == "Windows":
        base = "Win32GUI"
    
    setup(
        name="VMware vSphere Reporter Installer",
        version=args.version,
        description="Installationsassistent für VMware vSphere Reporter",
        options={"build_exe": build_exe_options},
        executables=[
            Executable(
                "build/installer_gui.py",
                base=base,
                target_name="VMware_vSphere_Reporter_Setup.exe",
                icon="build/images/logo_bechtle.png" if os.path.exists("build/images/logo_bechtle.png") else None,
                copyright="© 2025 Bechtle GmbH"
            )
        ]
    )
    
    # Erstellte Dateien in das angegebene Ausgabeverzeichnis verschieben
    output_dir = args.outdir
    os.makedirs(output_dir, exist_ok=True)
    
    # Finde den Build-Ordner, der von cx_Freeze erstellt wurde
    build_folder = None
    for item in os.listdir("build"):
        if item.startswith("exe."):
            build_folder = os.path.join("build", item)
            break
    
    if build_folder:
        # Erstelle ZIP- oder Installer-Paket
        if platform.system() == "Windows":
            try:
                # Versuche, NSIS zu verwenden, wenn verfügbar
                print("Versuche, NSIS-Installer zu erstellen (wenn NSIS installiert ist)...")
                nsis_script = create_nsis_script(build_folder, args.version)
                
                # Speichere NSIS-Skript
                with open("build/installer.nsi", "w") as f:
                    f.write(nsis_script)
                
                # Führe NSIS aus, wenn verfügbar
                try:
                    subprocess.run(["makensis", "build/installer.nsi"], check=True)
                    print(f"NSIS-Installer wurde erstellt: VMware_vSphere_Reporter_Setup_{args.version}.exe")
                except (subprocess.SubprocessError, FileNotFoundError):
                    print("NSIS nicht gefunden. Erstelle stattdessen ZIP-Paket...")
                    create_zip_package(build_folder, output_dir, args.version)
            except Exception as e:
                print(f"Fehler bei der NSIS-Erstellung: {str(e)}")
                create_zip_package(build_folder, output_dir, args.version)
        else:
            # Für nicht-Windows-Systeme immer ZIP verwenden
            create_zip_package(build_folder, output_dir, args.version)
    else:
        print("Fehler: Build-Ordner nicht gefunden!")
        return 1
    
    print("\nInstallationspaket-Erstellung abgeschlossen!")
    print(f"Die Dateien befinden sich im Verzeichnis: {output_dir}")
    return 0

def create_zip_package(build_folder, output_dir, version):
    """Erstellt ein ZIP-Paket mit den Installationsdateien"""
    import zipfile
    
    zip_name = os.path.join(output_dir, f"VMware_vSphere_Reporter_Installer_{version}.zip")
    print(f"Erstelle ZIP-Paket: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, build_folder)
                zipf.write(file_path, arcname)
    
    print(f"ZIP-Paket erstellt: {zip_name}")

def create_nsis_script(build_folder, version):
    """Generiert ein NSIS-Skript für die Erstellung eines Windows-Installers"""
    # NSIS-Skriptvorlage mit Bechtle-Branding
    script = f"""
; VMware vSphere Reporter Installer NSIS Script
; Generated by installer_builder.py

!include "MUI2.nsh"
!include "FileFunc.nsh"

; Metadaten
Name "VMware vSphere Reporter"
OutFile "VMware_vSphere_Reporter_Setup_{version}.exe"
InstallDir "$PROGRAMFILES\\Bechtle\\VMware vSphere Reporter"
InstallDirRegKey HKCU "Software\\Bechtle\\VMware vSphere Reporter" ""
RequestExecutionLevel admin

; Bechtle-Farbdefinitionen
!define BECHTLE_DARK_BLUE "0x00355E"
!define BECHTLE_ORANGE "0xDA6F1E"

; Moderne UI-Konfiguration
!define MUI_ABORTWARNING
!define MUI_ICON "{build_folder}\\images\\logo_bechtle.png"
!define MUI_UNICON "{build_folder}\\images\\logo_bechtle.png"

; UI-Anpassungen für Bechtle-Design
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "{build_folder}\\images\\logo_bechtle.png"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_WELCOMEFINISHPAGE_BITMAP "{build_folder}\\images\\logo_bechtle.png"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "{build_folder}\\images\\logo_bechtle.png"

!define MUI_WELCOMEPAGE_TITLE "Willkommen beim VMware vSphere Reporter Installer"
!define MUI_WELCOMEPAGE_TEXT "Dieser Assistent führt Sie durch die Installation des VMware vSphere Reporters.$\\r$\\n$\\r$\\nDer VMware vSphere Reporter ist ein leistungsstarkes Tool zur Erstellung umfassender Berichte über Ihre VMware-Umgebung.$\\r$\\n$\\r$\\n$_CLICK"

; Installationsseiten
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "build\\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Deinstallationsseiten
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Sprachdateien
!insertmacro MUI_LANGUAGE "German"

; Installationsabschnitt
Section "VMware vSphere Reporter" SecMain
    SetOutPath "$INSTDIR"
    
    ; Kopiere alle Dateien aus dem Build-Verzeichnis
    File /r "{build_folder}\\*.*"
    
    ; Speichere Installationsinformationen
    WriteRegStr HKCU "Software\\Bechtle\\VMware vSphere Reporter" "" $INSTDIR
    
    ; Erstelle Uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    ; Erstelle Startmenü-Einträge
    CreateDirectory "$SMPROGRAMS\\Bechtle"
    CreateDirectory "$SMPROGRAMS\\Bechtle\\VMware vSphere Reporter"
    CreateShortcut "$SMPROGRAMS\\Bechtle\\VMware vSphere Reporter\\VMware vSphere Reporter.lnk" "$INSTDIR\\VMware_vSphere_Reporter_Setup.exe"
    CreateShortcut "$SMPROGRAMS\\Bechtle\\VMware vSphere Reporter\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    ; Erstelle Desktop-Verknüpfung
    CreateShortcut "$DESKTOP\\VMware vSphere Reporter.lnk" "$INSTDIR\\VMware_vSphere_Reporter_Setup.exe"
SectionEnd

; Deinstallationsabschnitt
Section "Uninstall"
    ; Entferne Dateien und Verzeichnisse
    RMDir /r "$INSTDIR"
    
    ; Entferne Startmenü-Einträge
    RMDir /r "$SMPROGRAMS\\Bechtle\\VMware vSphere Reporter"
    RMDir "$SMPROGRAMS\\Bechtle" ; Nur entfernen, wenn leer
    
    ; Entferne Desktop-Verknüpfung
    Delete "$DESKTOP\\VMware vSphere Reporter.lnk"
    
    ; Entferne Registry-Einträge
    DeleteRegKey HKCU "Software\\Bechtle\\VMware vSphere Reporter"
SectionEnd
"""
    
    # Erstelle eine einfache LICENSE.txt, wenn nicht vorhanden
    if not os.path.exists("build/LICENSE.txt"):
        with open("build/LICENSE.txt", "w") as f:
            f.write("""VMware vSphere Reporter - Lizenzvereinbarung

Copyright (c) 2025 Bechtle GmbH

Alle Rechte vorbehalten.

Diese Software darf nur von autorisierten Benutzern verwendet werden.
Eine Weitergabe an Dritte ist ohne ausdrückliche Genehmigung nicht gestattet.
""")
    
    return script

if __name__ == "__main__":
    sys.exit(main())