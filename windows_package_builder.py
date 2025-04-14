#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Windows-Paketersteller

Dieses Skript erstellt ein vollständiges Windows-Installationspaket (.msi) für den VMware vSphere Reporter.
Das Paket enthält:
- Automatische Python-Installation (falls erforderlich)
- Alle benötigten Abhängigkeiten
- Kompilierte EXE-Dateien für Anwendungsstart ohne sichtbare Python-Umgebung
- Windows-Registry-Einträge und Verknüpfungen
- Bechtle-Branding

Abhängigkeiten:
- cx_Freeze
- setuptools
- wheel
- PyInstaller (optional)
"""

import os
import sys
import shutil
import platform
import subprocess
import tempfile
import argparse
import zipfile
import urllib.request
import logging
from pathlib import Path
from cx_Freeze import setup, Executable

# Konfiguration
PYTHON_EMBEDDED_URL = "https://www.python.org/ftp/python/3.10.8/python-3.10.8-embed-amd64.zip"
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
VERSION = "1.0.0"
COMPANY_NAME = "Bechtle GmbH"
COPYRIGHT = "© 2025 Bechtle GmbH"
PRODUCT_NAME = "VMware vSphere Reporter"

# Logger-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("package_builder.log", mode='w')
    ]
)
logger = logging.getLogger("package_builder")

def download_file(url, destination):
    """Lädt eine Datei von einer URL herunter"""
    logger.info(f"Herunterladen von {url} nach {destination}")
    try:
        urllib.request.urlretrieve(url, destination)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Herunterladen von {url}: {str(e)}")
        return False

def extract_zip(zip_path, extract_to):
    """Extrahiert eine ZIP-Datei"""
    logger.info(f"Extrahieren von {zip_path} nach {extract_to}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren von {zip_path}: {str(e)}")
        return False

def run_command(cmd, cwd=None, env=None):
    """Führt einen Befehl aus und protokolliert Ausgabe"""
    logger.info(f"Ausführen: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
            env=env
        )
        stdout, stderr = process.communicate()
        
        if stdout:
            logger.info(f"Ausgabe: {stdout}")
        if stderr:
            logger.error(f"Fehler: {stderr}")
            
        return process.returncode == 0
    except Exception as e:
        logger.error(f"Fehler bei Ausführung von {cmd}: {str(e)}")
        return False

def prepare_embedded_python(work_dir):
    """Bereitet eine eingebettete Python-Umgebung vor"""
    logger.info("Vorbereiten der eingebetteten Python-Umgebung")
    
    python_dir = os.path.join(work_dir, "python")
    os.makedirs(python_dir, exist_ok=True)
    
    python_zip = os.path.join(work_dir, "python_embedded.zip")
    
    # Python herunterladen
    if not download_file(PYTHON_EMBEDDED_URL, python_zip):
        return None
    
    # Python extrahieren
    if not extract_zip(python_zip, python_dir):
        return None
    
    # get-pip.py herunterladen und ausführen
    get_pip_path = os.path.join(python_dir, "get-pip.py")
    if not download_file(GET_PIP_URL, get_pip_path):
        return None
    
    # python310._pth anpassen (für pip-Unterstützung)
    pth_file = None
    for file in os.listdir(python_dir):
        if file.endswith("._pth"):
            pth_file = os.path.join(python_dir, file)
            break
    
    if pth_file:
        with open(pth_file, 'r') as f:
            content = f.read()
        
        # Kommentarzeichen vor import site entfernen
        if "#import site" in content:
            content = content.replace("#import site", "import site")
            
            with open(pth_file, 'w') as f:
                f.write(content)
    
    # Pip installieren
    python_exe = os.path.join(python_dir, "python.exe")
    if not run_command([python_exe, get_pip_path], cwd=python_dir):
        return None
    
    # Pfad zu Scripts-Verzeichnis und pip.exe
    scripts_dir = os.path.join(python_dir, "Scripts")
    pip_exe = os.path.join(scripts_dir, "pip.exe")
    
    # Abhängigkeiten installieren
    requirements = [
        "pyVmomi>=7.0.0",
        "PyQt5>=5.15.0", 
        "reportlab>=3.6.0", 
        "python-docx>=0.8.11", 
        "jinja2>=3.0.0", 
        "humanize>=3.0.0",
        "six>=1.16.0",
        "requests>=2.25.0",
        "cx_Freeze>=6.11.0",  # Für das Erstellen der EXE-Dateien
        "pywin32>=300"  # Für Windows-Verknüpfungen
    ]
    
    for req in requirements:
        if not run_command([pip_exe, "install", req], cwd=python_dir):
            logger.warning(f"Probleme bei der Installation von {req}")
    
    return {
        "python_exe": python_exe,
        "pip_exe": pip_exe,
        "python_dir": python_dir
    }

def create_embedded_setup_script(work_dir, python_info):
    """Erstellt ein Einbettungs-Skript für die ausführbare Datei"""
    template = """
import os
import sys
import subprocess
import tempfile
import zipfile
import urllib.request
import shutil

def error_message(title, message):
    """Zeigt eine Fehlermeldung an"""
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)

def info_message(title, message):
    """Zeigt eine Informationsmeldung an"""
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)

def is_admin():
    """Prüft, ob Administratorrechte vorhanden sind"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Startet das Programm mit Administratorrechten neu"""
    import sys
    import win32con
    import win32event
    import win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

    python_exe = sys.executable
    script = sys.argv[0]
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])

    proc_info = ShellExecuteEx(
        nShow=win32con.SW_SHOWNORMAL,
        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
        lpVerb='runas',
        lpFile=python_exe,
        lpParameters=script + ' ' + params
    )

    win32event.WaitForSingleObject(proc_info['hProcess'], -1)
    sys.exit(0)

def install_embedded_python():
    """Installiert Python und die Abhängigkeiten im temporären Verzeichnis"""
    # Temporäres Verzeichnis für Python erstellen
    temp_dir = tempfile.mkdtemp(prefix="vsphere_reporter_")
    
    # Eingebettetes Python extrahieren
    embedded_zip = os.path.join(os.path.dirname(sys.executable), "python_embedded.zip")
    if not os.path.exists(embedded_zip):
        error_message("Installationsfehler", 
                    "Eingebettete Python-Umgebung nicht gefunden. Bitte erneut installieren.")
        return None
    
    # Python extrahieren
    try:
        with zipfile.ZipFile(embedded_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    except Exception as e:
        error_message("Entpackungsfehler", 
                    f"Fehler beim Entpacken von Python: {str(e)}")
        return None
    
    python_exe = os.path.join(temp_dir, "python.exe")
    if not os.path.exists(python_exe):
        error_message("Installationsfehler", 
                    "Python-Executable nicht gefunden. Bitte erneut installieren.")
        return None
    
    return {
        "python_exe": python_exe,
        "python_dir": temp_dir
    }

def main():
    """Hauptfunktion für die Anwendung"""
    try:
        # Prüfe, ob volle Installation oder portable Version
        full_install = os.path.exists(os.path.join(os.path.dirname(sys.executable), "python_embedded.zip"))
        
        if full_install:
            # Bei voller Installation: Eingebettetes Python verwenden
            python_info = install_embedded_python()
            if not python_info:
                sys.exit(1)
            
            # Vorbereiten der Umgebungsvariablen
            env = os.environ.copy()
            env["PATH"] = python_info["python_dir"] + os.pathsep + env.get("PATH", "")
            
            # Hauptskript ausführen
            main_script = os.path.join(os.path.dirname(sys.executable), "vsphere_reporter.py")
            if not os.path.exists(main_script):
                error_message("Skriptfehler", 
                            "Hauptanwendungsskript nicht gefunden. Bitte erneut installieren.")
                sys.exit(1)
            
            # Python-Skript mit eingebettetem Python ausführen
            subprocess.Popen([python_info["python_exe"], main_script], env=env)
            
            # Temporäres Verzeichnis später aufräumen
            # (wird nicht sofort gelöscht, da die Anwendung es noch benötigt)
        else:
            # Bei portable Version: Integriertes Python im App-Verzeichnis suchen
            app_dir = os.path.dirname(sys.executable)
            python_dir = os.path.join(app_dir, "python")
            if not os.path.exists(python_dir):
                error_message("Konfigurationsfehler", 
                            "Python-Umgebung nicht gefunden. Bitte erneut installieren.")
                sys.exit(1)
            
            python_exe = os.path.join(python_dir, "python.exe")
            if not os.path.exists(python_exe):
                error_message("Konfigurationsfehler", 
                            "Python-Executable nicht gefunden. Bitte erneut installieren.")
                sys.exit(1)
            
            # Vorbereiten der Umgebungsvariablen
            env = os.environ.copy()
            env["PATH"] = python_dir + os.pathsep + env.get("PATH", "")
            
            # Hauptskript ausführen
            main_script = os.path.join(app_dir, "vsphere_reporter.py")
            if not os.path.exists(main_script):
                error_message("Skriptfehler", 
                            "Hauptanwendungsskript nicht gefunden. Bitte erneut installieren.")
                sys.exit(1)
            
            # Python-Skript mit eingebettetem Python ausführen
            subprocess.Popen([python_exe, main_script], env=env)
    
    except Exception as e:
        error_message("Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Prüfe, ob Admin-Rechte erforderlich sind und starte gegebenenfalls neu
    if sys.argv[-1] != "--no-admin-check" and not is_admin():
        run_as_admin()
    else:
        main()
"""
    
    # Speichern des Skripts
    script_path = os.path.join(work_dir, "embedded_launcher.py")
    with open(script_path, 'w') as f:
        f.write(template)
    
    return script_path

def create_windows_executable(work_dir, python_info, source_dir):
    """Erstellt die Windows-ausführbare Datei mit cx_Freeze"""
    logger.info("Erstellen der Windows-ausführbaren Datei")
    
    # Embedded-Launcher erstellen
    launcher_script = create_embedded_setup_script(work_dir, python_info)
    
    # Kopieren der Anwendungsdateien ins Build-Verzeichnis
    build_dir = os.path.join(work_dir, "build")
    os.makedirs(build_dir, exist_ok=True)
    
    for item in os.listdir(source_dir):
        src_path = os.path.join(source_dir, item)
        dst_path = os.path.join(build_dir, item)
        
        if os.path.isdir(src_path):
            if not os.path.exists(dst_path):
                shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    
    # Packen der eingebetteten Python-Umgebung für den Launcher
    embedded_zip = os.path.join(build_dir, "python_embedded.zip")
    with zipfile.ZipFile(embedded_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(python_info["python_dir"]):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, python_info["python_dir"])
                zipf.write(file_path, arcname)
    
    # Icon-Pfad finden
    icon_path = None
    possible_icon_paths = [
        os.path.join(source_dir, "images", "logo_bechtle.png"),
        os.path.join(source_dir, "attached_assets", "logo_bechtle.png")
    ]
    
    for path in possible_icon_paths:
        if os.path.exists(path):
            icon_path = path
            break
    
    # Verwende cx_Freeze, um die ausführbare Datei zu erstellen
    os.chdir(work_dir)
    
    build_exe_options = {
        "packages": ["os", "sys", "subprocess", "tempfile", "zipfile", "urllib.request", "shutil"],
        "excludes": ["tkinter", "unittest", "email", "http", "xml", "pydoc"],
        "include_files": [
            (embedded_zip, "python_embedded.zip"),
            (os.path.join(build_dir, "vsphere_reporter.py"), "vsphere_reporter.py"),
            (os.path.join(build_dir, "core"), "core"),
            (os.path.join(build_dir, "gui"), "gui"),
            (os.path.join(build_dir, "utils"), "utils"),
            (os.path.join(build_dir, "templates"), "templates"),
            (os.path.join(build_dir, "images"), "images") if os.path.exists(os.path.join(build_dir, "images")) else None,
            (os.path.join(build_dir, "docs"), "docs") if os.path.exists(os.path.join(build_dir, "docs")) else None,
        ],
        "include_msvcr": True,
    }
    
    # Entferne None-Einträge aus include_files
    build_exe_options["include_files"] = [item for item in build_exe_options["include_files"] if item is not None]
    
    # cx_Freeze-Setup
    executables = [
        Executable(
            script=launcher_script,
            target_name="VMwareVSphereReporter.exe",
            base="Win32GUI",  # Keine Konsole anzeigen
            icon=icon_path,
            copyright=COPYRIGHT
        )
    ]
    
    # Ausführen des Build-Prozesses
    setup(
        name=PRODUCT_NAME,
        version=VERSION,
        description="VMware vSphere Reporter - Comprehensive reporting tool",
        options={"build_exe": build_exe_options},
        executables=executables
    )
    
    # Finde das erzeugte Build-Verzeichnis
    output_dir = None
    for item in os.listdir(os.path.join(work_dir, "build")):
        if item.startswith("exe."):
            output_dir = os.path.join(work_dir, "build", item)
            break
    
    if not output_dir:
        logger.error("Build-Verzeichnis nicht gefunden")
        return None
    
    logger.info(f"Windows-ausführbare Datei erstellt in: {output_dir}")
    return output_dir

def create_msi_installer(work_dir, exe_dir, output_dir, source_dir):
    """Erstellt ein MSI-Installationspaket mit WiX Toolset"""
    logger.info("Erstellen des MSI-Installationspakets")
    
    # Prüfe, ob WiX Toolset verfügbar ist
    wix_available = False
    try:
        result = subprocess.run(["candle", "--version"], capture_output=True, text=True)
        wix_available = result.returncode == 0
    except FileNotFoundError:
        logger.warning("WiX Toolset nicht gefunden - keine MSI-Erstellung möglich")
    
    if not wix_available:
        logger.info("Erstelle stattdessen ein ZIP-Paket der ausführbaren Datei")
        return create_portable_zip(exe_dir, output_dir)
    
    # WiX-Projekt konfigurieren
    wix_dir = os.path.join(work_dir, "wix")
    os.makedirs(wix_dir, exist_ok=True)
    
    # Icon-Pfad finden
    icon_path = None
    possible_icon_paths = [
        os.path.join(source_dir, "images", "logo_bechtle.png"),
        os.path.join(source_dir, "attached_assets", "logo_bechtle.png")
    ]
    
    for path in possible_icon_paths:
        if os.path.exists(path):
            icon_path = path
            break
    
    # WiX-Produktdefinition erstellen
    product_wxs = f"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" 
             Name="{PRODUCT_NAME}" 
             Language="1033" 
             Version="{VERSION}" 
             Manufacturer="{COMPANY_NAME}" 
             UpgradeCode="12345678-1234-1234-1234-123456789012">
        
        <Package InstallerVersion="200" 
                 Compressed="yes" 
                 InstallScope="perMachine" 
                 Description="{PRODUCT_NAME} - VMware vSphere environment reporting tool" />

        <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
        <MediaTemplate EmbedCab="yes" />

        <Icon Id="ProductIcon" SourceFile="{icon_path or 'icon.ico'}" />
        <Property Id="ARPPRODUCTICON" Value="ProductIcon" />
        
        <Feature Id="ProductFeature" Title="{PRODUCT_NAME}" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
            <ComponentGroupRef Id="ProductShortcuts" />
        </Feature>
        
        <UIRef Id="WixUI_InstallDir" />
        <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
        <WixVariable Id="WixUILicenseRtf" Value="license.rtf" />
    </Product>

    <Fragment>
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="CompanyFolder" Name="{COMPANY_NAME}">
                    <Directory Id="INSTALLFOLDER" Name="{PRODUCT_NAME}" />
                </Directory>
            </Directory>
            <Directory Id="ProgramMenuFolder">
                <Directory Id="ApplicationProgramsFolder" Name="{COMPANY_NAME}" />
            </Directory>
            <Directory Id="DesktopFolder" Name="Desktop" />
        </Directory>
    </Fragment>

    <Fragment>
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            <!-- Dateien aus dem Build-Verzeichnis hinzufügen -->
        </ComponentGroup>
        
        <ComponentGroup Id="ProductShortcuts" Directory="ApplicationProgramsFolder">
            <Component Id="ApplicationShortcut" Guid="*">
                <Shortcut Id="ApplicationStartMenuShortcut" 
                          Name="{PRODUCT_NAME}" 
                          Description="VMware vSphere environment reporting tool"
                          Target="[INSTALLFOLDER]VMwareVSphereReporter.exe"
                          WorkingDirectory="INSTALLFOLDER" />
                <RemoveFolder Id="RemoveApplicationProgramsFolder" On="uninstall" />
                <RegistryValue Root="HKCU" 
                               Key="Software\\{COMPANY_NAME}\\{PRODUCT_NAME}" 
                               Name="installed" 
                               Type="integer" 
                               Value="1" 
                               KeyPath="yes" />
            </Component>
            
            <Component Id="DesktopShortcut" Guid="*">
                <Shortcut Id="ApplicationDesktopShortcut" 
                          Name="{PRODUCT_NAME}" 
                          Description="VMware vSphere environment reporting tool"
                          Target="[INSTALLFOLDER]VMwareVSphereReporter.exe"
                          WorkingDirectory="INSTALLFOLDER" />
                <RegistryValue Root="HKCU" 
                               Key="Software\\{COMPANY_NAME}\\{PRODUCT_NAME}" 
                               Name="desktop_shortcut" 
                               Type="integer" 
                               Value="1" 
                               KeyPath="yes" />
            </Component>
        </ComponentGroup>
    </Fragment>
</Wix>
"""
    
    # WiX-Produktdefinition speichern
    product_wxs_path = os.path.join(wix_dir, "product.wxs")
    with open(product_wxs_path, 'w') as f:
        f.write(product_wxs)
    
    # Minimale Lizenzdatei erstellen
    license_rtf_path = os.path.join(wix_dir, "license.rtf")
    with open(license_rtf_path, 'w') as f:
        f.write(r"{\rtf1\ansi\deff0{\fonttbl{\f0\fnil\fcharset0 Arial;}}{\colortbl;\red0\green0\blue0;}\viewkind4\uc1\pard\cf1\lang1033\fs20 VMware vSphere Reporter\par\par Copyright (c) 2025 Bechtle GmbH\par\par All rights reserved.\par}")
    
    # WiX-Befehle ausführen
    # 1. candle (kompilieren)
    candle_cmd = ["candle", "-o", os.path.join(wix_dir, "product.wixobj"), product_wxs_path]
    if not run_command(candle_cmd, cwd=wix_dir):
        logger.error("Fehler beim Kompilieren des WiX-Projekts")
        return create_portable_zip(exe_dir, output_dir)
    
    # 2. light (linken)
    light_cmd = [
        "light",
        "-ext", "WixUIExtension",
        "-o", os.path.join(output_dir, f"{PRODUCT_NAME.replace(' ', '')}_Setup_{VERSION}.msi"),
        os.path.join(wix_dir, "product.wixobj")
    ]
    if not run_command(light_cmd, cwd=wix_dir):
        logger.error("Fehler beim Linken des WiX-Projekts")
        return create_portable_zip(exe_dir, output_dir)
    
    logger.info(f"MSI-Installationspaket erstellt in: {output_dir}")
    return os.path.join(output_dir, f"{PRODUCT_NAME.replace(' ', '')}_Setup_{VERSION}.msi")

def create_portable_zip(exe_dir, output_dir):
    """Erstellt ein portables ZIP-Archiv aus dem EXE-Verzeichnis"""
    logger.info("Erstellen eines portablen ZIP-Archivs")
    
    zip_path = os.path.join(output_dir, f"{PRODUCT_NAME.replace(' ', '')}_Portable_{VERSION}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(exe_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, exe_dir)
                zipf.write(file_path, arcname)
    
    logger.info(f"Portables ZIP-Archiv erstellt: {zip_path}")
    return zip_path

def create_portable_version(work_dir, python_info, source_dir, output_dir):
    """Erstellt eine portable Version mit eingebettetem Python"""
    logger.info("Erstellen einer portablen Version mit eingebettetem Python")
    
    portable_dir = os.path.join(work_dir, "portable")
    os.makedirs(portable_dir, exist_ok=True)
    
    # App-Verzeichnis erstellen
    app_dir = os.path.join(portable_dir, PRODUCT_NAME)
    os.makedirs(app_dir, exist_ok=True)
    
    # Python-Umgebung kopieren
    python_dir = os.path.join(app_dir, "python")
    shutil.copytree(python_info["python_dir"], python_dir)
    
    # Anwendungsdateien kopieren
    for item in os.listdir(source_dir):
        src_path = os.path.join(source_dir, item)
        dst_path = os.path.join(app_dir, item)
        
        if os.path.isdir(src_path):
            if not os.path.exists(dst_path):
                shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    
    # Launcher-Skript erstellen
    launcher_script = os.path.join(app_dir, "launcher.py")
    with open(launcher_script, 'w') as f:
        f.write("""
import os
import sys
import subprocess

def main():
    # Pfade vorbereiten
    app_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = os.path.join(app_dir, "python", "python.exe")
    vsphere_script = os.path.join(app_dir, "vsphere_reporter.py")
    
    # Prüfen, ob alles vorhanden ist
    if not os.path.exists(python_exe):
        print("Fehler: Python-Executable nicht gefunden")
        return 1
        
    if not os.path.exists(vsphere_script):
        print("Fehler: Hauptanwendungsskript nicht gefunden")
        return 1
    
    # Umgebungsvariablen vorbereiten
    env = os.environ.copy()
    env["PATH"] = os.path.join(app_dir, "python") + os.pathsep + env.get("PATH", "")
    
    # Anwendung starten
    subprocess.Popen([python_exe, vsphere_script], env=env)
    return 0

if __name__ == "__main__":
    sys.exit(main())
""")
    
    # Batch-Datei für einfachen Start erstellen
    batch_file = os.path.join(app_dir, "VMwareVSphereReporter.bat")
    with open(batch_file, 'w') as f:
        f.write(f"""@echo off
cd /d "%~dp0"
pythonw launcher.py
""")
    
    # Alles in ein ZIP-Archiv packen
    zip_path = os.path.join(output_dir, f"{PRODUCT_NAME.replace(' ', '')}_Portable_{VERSION}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, portable_dir)
                zipf.write(file_path, arcname)
    
    logger.info(f"Portable Version erstellt: {zip_path}")
    return zip_path

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="VMware vSphere Reporter - Windows-Paketersteller")
    parser.add_argument('--source', default='.', help='Quellverzeichnis mit den Anwendungsdateien')
    parser.add_argument('--output', default='dist', help='Ausgabeverzeichnis für die erstellten Pakete')
    parser.add_argument('--temp', default=None, help='Temporäres Arbeitsverzeichnis (standardmäßig automatisch erstellt)')
    parser.add_argument('--portable', action='store_true', help='Nur portable Version erstellen')
    args = parser.parse_args()
    
    # Prüfen, ob wir auf Windows sind
    if platform.system() != "Windows":
        logger.warning("Dieses Skript ist für Windows optimiert. Die Erstellung auf anderen Plattformen kann fehlschlagen.")
    
    # Arbeitsverzeichnis vorbereiten
    work_dir = args.temp or tempfile.mkdtemp(prefix="vsphere_build_")
    logger.info(f"Arbeitsverzeichnis: {work_dir}")
    
    # Ausgabeverzeichnis erstellen
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Ausgabeverzeichnis: {output_dir}")
    
    # Quellverzeichnis normalisieren
    source_dir = os.path.abspath(args.source)
    logger.info(f"Quellverzeichnis: {source_dir}")
    
    try:
        # Eingebettete Python-Umgebung vorbereiten
        logger.info("Vorbereiten der Python-Umgebung...")
        python_info = prepare_embedded_python(work_dir)
        if not python_info:
            logger.error("Fehler bei der Vorbereitung der Python-Umgebung")
            return 1
        
        if args.portable:
            # Nur portable Version erstellen
            logger.info("Erstellen einer portablen Version...")
            portable_path = create_portable_version(work_dir, python_info, source_dir, output_dir)
            if not portable_path:
                logger.error("Fehler bei der Erstellung der portablen Version")
                return 1
            
            logger.info(f"Portable Version erfolgreich erstellt: {portable_path}")
            return 0
        
        # Windows-ausführbare Datei erstellen
        logger.info("Erstellen der Windows-ausführbaren Datei...")
        exe_dir = create_windows_executable(work_dir, python_info, source_dir)
        if not exe_dir:
            logger.error("Fehler bei der Erstellung der Windows-ausführbaren Datei")
            return 1
        
        # MSI-Installationspaket erstellen
        logger.info("Erstellen des MSI-Installationspakets...")
        msi_path = create_msi_installer(work_dir, exe_dir, output_dir, source_dir)
        if not msi_path:
            logger.error("Fehler bei der Erstellung des MSI-Installationspakets")
            return 1
        
        # Erfolgreiche Beendigung
        logger.info("Paketerstellung abgeschlossen!")
        logger.info(f"Erstellte Dateien befinden sich in: {output_dir}")
        return 0
        
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {str(e)}", exc_info=True)
        return 1
    finally:
        # Aufräumen, falls gewünscht
        if not args.temp:  # Nur automatisch erstellte Verzeichnisse löschen
            logger.info(f"Aufräumen des Arbeitsverzeichnisses: {work_dir}")
            try:
                shutil.rmtree(work_dir)
            except Exception as e:
                logger.warning(f"Fehler beim Aufräumen: {str(e)}")

if __name__ == "__main__":
    sys.exit(main())