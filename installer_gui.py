#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Grafischer Installer
Ein moderner Installationsassistent im Bechtle-Design

Copyright (c) 2025 Bechtle GmbH
"""
import os
import sys
import subprocess
import platform
import logging
import threading
import time
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWizard, QWizardPage, QLabel, QVBoxLayout,
                            QHBoxLayout, QPushButton, QRadioButton, QProgressBar,
                            QPlainTextEdit, QCheckBox, QLineEdit, QFileDialog,
                            QMessageBox, QGroupBox, QFormLayout, QGridLayout, QSpacerItem)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QFontMetrics
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal

# Bechtle-Farbschema
BECHTLE_DARK_BLUE = "#00355e"
BECHTLE_ORANGE = "#da6f1e"
BECHTLE_GREEN = "#23a96a"
BECHTLE_LIGHT_GRAY = "#f3f3f3"
BECHTLE_DARK_GRAY = "#5a5a5a"

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('installer')

class InstallationThread(QThread):
    """Thread für die Installation der Abhängigkeiten"""
    progress_update = pyqtSignal(str)
    progress_value = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, python_executable, install_path):
        """Initialisierung des Installationsthreads"""
        super().__init__()
        self.python_executable = python_executable
        self.install_path = install_path
        self.requirements = [
            "pyVmomi>=7.0.0",
            "PyQt5>=5.15.0", 
            "reportlab>=3.6.0", 
            "python-docx>=0.8.11", 
            "jinja2>=3.0.0", 
            "humanize>=3.0.0",
            "six>=1.16.0",
            "requests>=2.25.0"
        ]
        self.canceled = False
        
    def run(self):
        """Führt die Installation aus"""
        try:
            # Verzeichnisstruktur erstellen
            os.makedirs(os.path.join(self.install_path, 'logs'), exist_ok=True)
            self.progress_update.emit("Erstelle Verzeichnisstruktur...")
            self.progress_value.emit(10)
            
            # Requirements-Datei erstellen/prüfen
            req_path = os.path.join(self.install_path, 'vsphere_reporter_requirements.txt')
            if not os.path.exists(req_path):
                self.progress_update.emit("Erstelle Requirements-Datei...")
                with open(req_path, 'w') as f:
                    f.write('\n'.join(self.requirements))
                    
            # Basis-Fortschritt
            self.progress_value.emit(20)
            
            # Installation der Abhängigkeiten
            total_packages = len(self.requirements)
            for i, package in enumerate(self.requirements):
                if self.canceled:
                    self.finished.emit(False, "Installation abgebrochen")
                    return
                    
                progress = 20 + int((i / total_packages) * 70)
                self.progress_value.emit(progress)
                self.progress_update.emit(f"Installiere {package}...")
                
                try:
                    # pip install ausführen
                    cmd = [self.python_executable, "-m", "pip", "install", package]
                    process = subprocess.Popen(
                        cmd, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    stdout, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        logger.error(f"Fehler bei der Installation von {package}: {stderr}")
                        self.progress_update.emit(f"Fehler bei {package}: {stderr}")
                        time.sleep(1)  # Pause, damit Benutzer den Fehler sehen kann
                    else:
                        logger.info(f"{package} erfolgreich installiert")
                except Exception as e:
                    logger.error(f"Ausnahme bei der Installation von {package}: {str(e)}")
                    self.progress_update.emit(f"Fehler: {str(e)}")
            
            # Erstellung der Desktop-Verknüpfung
            self.progress_update.emit("Erstelle Desktop-Verknüpfung...")
            self.progress_value.emit(95)
            
            if platform.system() == "Windows":
                self._create_windows_shortcut()
            elif platform.system() == "Linux":
                self._create_linux_shortcut()
                
            # Fertig!
            self.progress_value.emit(100)
            self.progress_update.emit("Installation abgeschlossen!")
            self.finished.emit(True, "")
            
        except Exception as e:
            logger.error(f"Fehler bei der Installation: {str(e)}")
            self.progress_update.emit(f"Kritischer Fehler: {str(e)}")
            self.finished.emit(False, str(e))
    
    def _create_windows_shortcut(self):
        """Erstellt eine Windows-Verknüpfung auf dem Desktop"""
        try:
            import win32com.client
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "VMware vSphere Reporter.lnk")
            
            target_script = os.path.join(self.install_path, "vsphere_reporter.py")
            wdir = self.install_path
            icon = os.path.join(self.install_path, "images", "logo_bechtle.png")
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f'"{target_script}"'
            shortcut.WorkingDirectory = wdir
            shortcut.IconLocation = icon
            shortcut.save()
            
            self.progress_update.emit("Desktop-Verknüpfung erstellt")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Windows-Verknüpfung: {str(e)}")
            self.progress_update.emit("Warnung: Desktop-Verknüpfung konnte nicht erstellt werden")
    
    def _create_linux_shortcut(self):
        """Erstellt eine Linux .desktop-Datei"""
        try:
            # Desktop-Datei für Linux
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_dir):
                desktop_dir = os.path.join(os.path.expanduser("~"), "Schreibtisch")  # Deutsch
                
            desktop_file_path = os.path.join(desktop_dir, "vsphere-reporter.desktop")
            icon_path = os.path.join(self.install_path, "images", "logo_bechtle.png")
            
            with open(desktop_file_path, "w") as f:
                f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=VMware vSphere Reporter
Comment=Comprehensive reporting tool for VMware vSphere environments
Exec={sys.executable} "{os.path.join(self.install_path, 'vsphere_reporter.py')}"
Icon={icon_path}
Path={self.install_path}
Terminal=false
Categories=Utility;Development;
""")
            
            # Ausführbar machen
            os.chmod(desktop_file_path, 0o755)
            self.progress_update.emit("Desktop-Verknüpfung erstellt")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Linux-Verknüpfung: {str(e)}")
            self.progress_update.emit("Warnung: Desktop-Verknüpfung konnte nicht erstellt werden")
            
    def cancel(self):
        """Bricht die Installation ab"""
        self.canceled = True


class WelcomePage(QWizardPage):
    """Willkommensseite des Installationsassistenten"""
    def __init__(self, logo_path=None):
        super().__init__()
        self.setTitle("Willkommen beim VMware vSphere Reporter Installer")
        self.setSubTitle("Dieser Assistent führt Sie durch die Installation des VMware vSphere Reporters.")
        
        layout = QVBoxLayout()
        
        # Logo anzeigen
        if logo_path and os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # Breite auf max. 300px beschränken, Höhe proportional
            if pixmap.width() > 300:
                pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
            layout.addSpacing(20)
            
        # Bechtle-Header
        header_layout = QVBoxLayout()
        
        product_label = QLabel("VMware vSphere Reporter")
        product_label.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-size: 18pt; font-weight: bold;")
        product_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(product_label)
        
        subtitle_label = QLabel("Cloud Solutions | Datacenter & Endpoint")
        subtitle_label.setStyleSheet(f"color: {BECHTLE_DARK_GRAY}; font-size: 12pt;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-size: 10pt;")
        version_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(version_label)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # Willkommenstext
        welcome_text = QLabel(
            "<p>Der VMware vSphere Reporter ist ein leistungsstarkes Tool zur Erstellung umfassender "
            "Berichte über Ihre VMware-Umgebung. Mit diesem Assistenten werden alle erforderlichen "
            "Komponenten installiert.</p>"
            "<p>Klicken Sie auf 'Weiter', um fortzufahren.</p>"
        )
        welcome_text.setWordWrap(True)
        welcome_text.setStyleSheet(f"color: {BECHTLE_DARK_GRAY}; font-size: 11pt;")
        layout.addWidget(welcome_text)
        
        # Copyright-Info
        copyright_label = QLabel("© 2025 Bechtle GmbH")
        copyright_label.setStyleSheet(f"color: {BECHTLE_DARK_GRAY}; font-size: 9pt;")
        copyright_label.setAlignment(Qt.AlignRight)
        layout.addSpacing(20)
        layout.addWidget(copyright_label)
        
        self.setLayout(layout)


class PythonDetectionPage(QWizardPage):
    """Seite zur Python-Erkennung"""
    def __init__(self):
        super().__init__()
        self.setTitle("Python-Konfiguration")
        self.setSubTitle("Wählen Sie die zu verwendende Python-Installation")
        
        self.python_path = None
        self.detected_pythons = []
        
        layout = QVBoxLayout()
        
        # Erklärungstext
        info_label = QLabel(
            "VMware vSphere Reporter benötigt Python 3.8 oder höher. "
            "Wählen Sie aus den erkannten Python-Versionen oder geben Sie einen benutzerdefinierten Pfad an."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        layout.addWidget(info_label)
        layout.addSpacing(10)
        
        # Gruppierung der RadioButtons für Python-Versionen
        self.python_group = QGroupBox("Erkannte Python-Installationen")
        self.python_group_layout = QVBoxLayout()
        
        # Hinzufügen eines Labels während der Erkennung
        self.detecting_label = QLabel("Python-Installationen werden erkannt...")
        self.detecting_label.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-style: italic;")
        self.python_group_layout.addWidget(self.detecting_label)
        
        self.python_group.setLayout(self.python_group_layout)
        layout.addWidget(self.python_group)
        
        # Benutzerdefinierter Pfad
        self.custom_group = QGroupBox("Benutzerdefinierte Python-Installation")
        custom_layout = QHBoxLayout()
        
        self.custom_path = QLineEdit()
        self.custom_path.setPlaceholderText("Pfad zur Python-Executable...")
        custom_layout.addWidget(self.custom_path)
        
        browse_button = QPushButton("Durchsuchen...")
        browse_button.clicked.connect(self.browse_python)
        custom_layout.addWidget(browse_button)
        
        self.custom_group.setLayout(custom_layout)
        layout.addWidget(self.custom_group)
        
        # Status-Label für Validierung
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Validate-Button
        validate_button = QPushButton("Python-Version überprüfen")
        validate_button.clicked.connect(self.validate_python)
        validate_button.setStyleSheet(
            f"background-color: {BECHTLE_DARK_BLUE}; color: white; padding: 5px 10px;"
        )
        layout.addWidget(validate_button)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Starte Thread zur Python-Erkennung
        self.detect_thread = threading.Thread(target=self.detect_python_installations)
        self.detect_thread.daemon = True
        self.detect_thread.start()
        
    def initializePage(self):
        # Wird aufgerufen, wenn die Seite angezeigt wird
        self.registerField("python_executable*", self, "pythonExecutable", "pythonExecutableChanged")
    
    def detect_python_installations(self):
        """Erkennt installierte Python-Versionen"""
        try:
            self.detected_pythons = []
            
            # Standard-Python-Befehle prüfen
            commands = ["python", "python3", "py", "python3.8", "python3.9", "python3.10", "python3.11"]
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        [cmd, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        if self._is_valid_version(version):
                            self.detected_pythons.append((cmd, version))
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass
                
            # Unter Windows spezifische Pfade prüfen
            if platform.system() == "Windows":
                potential_paths = []
                
                # Standard-Installationspfade
                for version in ["38", "39", "310", "311"]:
                    paths = [
                        f"C:\\Python{version}\\python.exe",
                        f"C:\\Program Files\\Python{version}\\python.exe",
                        f"C:\\Program Files (x86)\\Python{version}\\python.exe",
                    ]
                    potential_paths.extend(paths)
                
                # AppData-Pfade
                appdata = os.environ.get("LOCALAPPDATA", "")
                for version in ["3.8", "3.9", "3.10", "3.11"]:
                    path = os.path.join(appdata, "Programs", f"Python", f"Python{version.replace('.', '')}", "python.exe")
                    potential_paths.append(path)
                
                # Windows Store Python
                for version in ["3.8", "3.9", "3.10", "3.11"]:
                    path = os.path.join(appdata, "Microsoft", "WindowsApps", f"python{version.replace('.', '')}.exe")
                    potential_paths.append(path)
                
                # Prüfe jeden Pfad
                for path in potential_paths:
                    if os.path.exists(path):
                        try:
                            result = subprocess.run(
                                [path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
                                capture_output=True, text=True, timeout=5
                            )
                            if result.returncode == 0:
                                version = result.stdout.strip()
                                if self._is_valid_version(version):
                                    self.detected_pythons.append((path, version))
                        except subprocess.SubprocessError:
                            pass
            
            # Aktualisiere die UI im Hauptthread
            QApplication.instance().processEvents()
            self._update_python_choices()
            
        except Exception as e:
            logger.error(f"Fehler bei der Python-Erkennung: {str(e)}")
    
    def _update_python_choices(self):
        """Aktualisiert die UI mit den erkannten Python-Versionen"""
        # Entferne das "Wird erkannt"-Label
        if self.detecting_label:
            self.detecting_label.setParent(None)
            self.detecting_label = None
        
        # Lösche eventuell vorhandene RadioButtons
        for i in reversed(range(self.python_group_layout.count())):
            widget = self.python_group_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Wenn keine Python-Version gefunden wurde
        if not self.detected_pythons:
            not_found_label = QLabel("Keine kompatible Python-Installation gefunden. Bitte geben Sie einen benutzerdefinierten Pfad an.")
            not_found_label.setStyleSheet(f"color: {BECHTLE_ORANGE};")
            self.python_group_layout.addWidget(not_found_label)
            return
        
        # Füge für jede erkannte Python-Version einen RadioButton hinzu
        for i, (path, version) in enumerate(self.detected_pythons):
            radio = QRadioButton(f"{path} (Version {version})")
            if i == 0:  # Erste Option vorauswählen
                radio.setChecked(True)
                self.python_path = path
            radio.clicked.connect(lambda checked, p=path: self._select_python(p))
            self.python_group_layout.addWidget(radio)
    
    def _select_python(self, path):
        """Speichert den ausgewählten Python-Pfad"""
        self.python_path = path
        self.setPythonExecutable(path)
        # Zurücksetzen des Status-Labels
        self.status_label.setText("")
    
    def validate_python(self):
        """Überprüft die ausgewählte Python-Version"""
        path = self.python_path
        
        # Wenn benutzerdefinierter Pfad eingegeben wurde
        if self.custom_path.text().strip():
            path = self.custom_path.text().strip()
        
        if not path:
            self.status_label.setText("Bitte wählen Sie eine Python-Installation aus oder geben Sie einen benutzerdefinierten Pfad an.")
            self.status_label.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-weight: bold;")
            return
        
        try:
            # Prüfe Python-Version
            result = subprocess.run(
                [path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                if self._is_valid_version(version):
                    self.status_label.setText(f"Python {version} wurde erfolgreich validiert! ✓")
                    self.status_label.setStyleSheet(f"color: {BECHTLE_GREEN}; font-weight: bold;")
                    self.python_path = path
                    self.setPythonExecutable(path)  # Feld aktualisieren
                    
                    # Prüfe Abhängigkeiten
                    self._check_dependencies(path)
                else:
                    self.status_label.setText(f"Python {version} ist zu alt. Bitte verwenden Sie Python 3.8 oder höher.")
                    self.status_label.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-weight: bold;")
            else:
                self.status_label.setText(f"Fehler bei der Überprüfung: {result.stderr}")
                self.status_label.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-weight: bold;")
                
        except Exception as e:
            self.status_label.setText(f"Fehler: {str(e)}")
            self.status_label.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-weight: bold;")
    
    def _check_dependencies(self, python_path):
        """Prüft, ob pip verfügbar ist"""
        try:
            # Prüfe pip
            result = subprocess.run(
                [python_path, "-m", "pip", "--version"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                self.status_label.setText(
                    f"{self.status_label.text()}\nPip wurde gefunden und ist einsatzbereit. ✓"
                )
            else:
                self.status_label.setText(
                    f"{self.status_label.text()}\nWarnung: Pip scheint nicht verfügbar zu sein. "
                    f"Die Installation der Abhängigkeiten könnte fehlschlagen."
                )
                
        except Exception as e:
            self.status_label.setText(
                f"{self.status_label.text()}\nWarnung: Pip-Status konnte nicht überprüft werden: {str(e)}"
            )
    
    def _is_valid_version(self, version_str):
        """Prüft, ob die Python-Version kompatibel ist (≥ 3.8)"""
        try:
            parts = version_str.split('.')
            major, minor = int(parts[0]), int(parts[1])
            return (major > 3) or (major == 3 and minor >= 8)
        except (ValueError, IndexError):
            return False
    
    def browse_python(self):
        """Öffnet einen Dateidialog zur Auswahl der Python-Executable"""
        options = QFileDialog.Options()
        if platform.system() == "Windows":
            caption = "Python-Executable auswählen"
            filter_str = "Python Executable (*.exe)"
        else:
            caption = "Python-Executable auswählen"
            filter_str = "All Files (*)"
            
        file_name, _ = QFileDialog.getOpenFileName(
            self, caption, "", filter_str, options=options
        )
        
        if file_name:
            self.custom_path.setText(file_name)
            self.python_path = file_name  # Aktualisiere den Python-Pfad
            
    def pythonExecutable(self):
        """Gibt den ausgewählten Python-Pfad zurück (für das Wizard-Feld)"""
        return self.python_path or ""
    
    def setPythonExecutable(self, path):
        """Setzt den Python-Pfad (für das Wizard-Feld)"""
        self.python_path = path
        self.completeChanged.emit()
    
    def isComplete(self):
        """Prüft, ob die Seite vollständig ausgefüllt ist"""
        return bool(self.python_path)


class InstallationPathPage(QWizardPage):
    """Seite zur Auswahl des Installationspfads"""
    def __init__(self):
        super().__init__()
        self.setTitle("Installationspfad")
        self.setSubTitle("Wählen Sie den Ordner, in dem VMware vSphere Reporter installiert werden soll")
        
        layout = QVBoxLayout()
        
        # Erklärungstext
        info_label = QLabel(
            "Bitte wählen Sie den Ordner aus, in dem der VMware vSphere Reporter installiert werden soll. "
            "Standardmäßig wird die Anwendung in Ihrem Benutzerverzeichnis installiert."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        layout.addWidget(info_label)
        layout.addSpacing(10)
        
        # Pfadauswahl
        path_layout = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        default_path = os.path.join(os.path.expanduser("~"), "VMware vSphere Reporter")
        self.path_edit.setText(default_path)
        path_layout.addWidget(self.path_edit)
        
        browse_button = QPushButton("Durchsuchen...")
        browse_button.clicked.connect(self.browse_directory)
        path_layout.addWidget(browse_button)
        
        layout.addLayout(path_layout)
        
        # Optionen
        options_group = QGroupBox("Installationsoptionen")
        options_layout = QVBoxLayout()
        
        self.create_shortcut = QCheckBox("Desktop-Verknüpfung erstellen")
        self.create_shortcut.setChecked(True)
        options_layout.addWidget(self.create_shortcut)
        
        self.add_to_start_menu = QCheckBox("Zum Startmenü hinzufügen (nur Windows)")
        self.add_to_start_menu.setChecked(True)
        if platform.system() != "Windows":
            self.add_to_start_menu.setEnabled(False)
        options_layout.addWidget(self.add_to_start_menu)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Speicherplatz-Info
        space_layout = QFormLayout()
        required_space = QLabel("~15 MB")
        required_space.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-weight: bold;")
        space_layout.addRow("Benötigter Speicherplatz:", required_space)
        
        self.available_space = QLabel("")
        self.update_available_space()
        space_layout.addRow("Verfügbarer Speicherplatz:", self.available_space)
        
        layout.addLayout(space_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Registriere Felder
        self.registerField("install_path*", self.path_edit)
        self.registerField("create_shortcut", self.create_shortcut)
        self.registerField("add_to_start_menu", self.add_to_start_menu)
        
        # Verbinde Signals
        self.path_edit.textChanged.connect(self.update_available_space)
    
    def update_available_space(self):
        """Aktualisiert die Anzeige des verfügbaren Speicherplatzes"""
        path = self.path_edit.text()
        if not path:
            self.available_space.setText("Unbekannt")
            return
            
        try:
            # Wenn der Pfad nicht existiert, verwende sein Elternverzeichnis
            check_path = path
            while not os.path.exists(check_path) and check_path != os.path.dirname(check_path):
                check_path = os.path.dirname(check_path)
                
            if not os.path.exists(check_path):
                self.available_space.setText("Unbekannt")
                return
                
            # Ermittle freien Speicherplatz
            if platform.system() == "Windows":
                free_bytes = shutil.disk_usage(check_path).free
            else:
                stat = os.statvfs(check_path)
                free_bytes = stat.f_frsize * stat.f_bavail
                
            # In lesbare Form umwandeln
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if free_bytes < 1024:
                    self.available_space.setText(f"{free_bytes:.1f} {unit}")
                    break
                free_bytes /= 1024
                
            # Farblich markieren, wenn wenig Platz vorhanden ist
            if free_bytes < 100 and unit == 'MB':  # Weniger als 100 MB
                self.available_space.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-weight: bold;")
            else:
                self.available_space.setStyleSheet(f"color: {BECHTLE_GREEN}; font-weight: bold;")
                
        except Exception as e:
            logger.error(f"Fehler bei der Ermittlung des freien Speicherplatzes: {str(e)}")
            self.available_space.setText("Fehler bei der Ermittlung")
            self.available_space.setStyleSheet(f"color: {BECHTLE_ORANGE};")
    
    def browse_directory(self):
        """Öffnet einen Dialog zur Auswahl des Installationsverzeichnisses"""
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(
            self, "Installationsverzeichnis auswählen", 
            self.path_edit.text(), options=options
        )
        
        if directory:
            # Falls der Benutzer nur ein Verzeichnis auswählt, füge den Anwendungsnamen hinzu
            if os.path.basename(directory) != "VMware vSphere Reporter":
                directory = os.path.join(directory, "VMware vSphere Reporter")
            self.path_edit.setText(directory)
    
    def validatePage(self):
        """Validiert den ausgewählten Pfad"""
        path = self.path_edit.text()
        
        # Prüfe, ob der Pfad gültig ist
        if not path:
            QMessageBox.warning(self, "Ungültiger Pfad", "Bitte geben Sie einen gültigen Installationspfad an.")
            return False
            
        # Prüfe, ob der Pfad zu lang ist (Windows-Einschränkung)
        if platform.system() == "Windows" and len(path) > 260:
            QMessageBox.warning(
                self, "Pfad zu lang", 
                "Der Pfad überschreitet die maximale Länge von 260 Zeichen unter Windows."
            )
            return False
            
        # Prüfe, ob im angegebenen Verzeichnis geschrieben werden kann
        parent_dir = os.path.dirname(path)
        if os.path.exists(path):
            # Verzeichnis existiert bereits - prüfe Schreibrechte
            if not os.access(path, os.W_OK):
                QMessageBox.warning(
                    self, "Keine Schreibrechte", 
                    f"Sie haben keine Schreibrechte für das Verzeichnis '{path}'."
                )
                return False
        elif os.path.exists(parent_dir):
            # Elternverzeichnis existiert - prüfe Schreibrechte
            if not os.access(parent_dir, os.W_OK):
                QMessageBox.warning(
                    self, "Keine Schreibrechte", 
                    f"Sie haben keine Schreibrechte für das Verzeichnis '{parent_dir}'."
                )
                return False
        else:
            # Weder Zielverzeichnis noch Elternverzeichnis existieren
            QMessageBox.warning(
                self, "Verzeichnis nicht gefunden", 
                f"Das Verzeichnis '{parent_dir}' existiert nicht."
            )
            return False
            
        return True


class InstallationPage(QWizardPage):
    """Seite für den eigentlichen Installationsprozess"""
    def __init__(self):
        super().__init__()
        self.setTitle("Installation")
        self.setSubTitle("Installation der Anwendung und Abhängigkeiten")
        
        self.install_thread = None
        
        layout = QVBoxLayout()
        
        # Fortschrittsbalken
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Statustext
        self.status_label = QLabel("Bereit zur Installation...")
        layout.addWidget(self.status_label)
        
        # Detailed log
        log_group = QGroupBox("Installationsprotokoll")
        log_layout = QVBoxLayout()
        
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Optionen unten
        bottom_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.cancel_installation)
        bottom_layout.addWidget(self.cancel_button)
        
        bottom_layout.addStretch()
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Wird aufgerufen, wenn die Seite angezeigt wird"""
        # Parameter aus den vorherigen Seiten abrufen
        python_exec = self.field("python_executable")
        install_path = self.field("install_path")
        
        # Log mit Basisinformationen
        self.log_text.clear()
        self.log("Installation wird vorbereitet...")
        self.log(f"Python: {python_exec}")
        self.log(f"Installationspfad: {install_path}")
        
        # Starte den Installationsprozess
        self.install_thread = InstallationThread(python_exec, install_path)
        self.install_thread.progress_update.connect(self.update_status)
        self.install_thread.progress_value.connect(self.update_progress)
        self.install_thread.finished.connect(self.installation_finished)
        self.install_thread.start()
    
    def log(self, message):
        """Fügt eine Nachricht zum Installationsprotokoll hinzu"""
        self.log_text.appendPlainText(f"[{time.strftime('%H:%M:%S')}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def update_status(self, message):
        """Aktualisiert den Statustext und das Log"""
        self.status_label.setText(message)
        self.log(message)
    
    def update_progress(self, value):
        """Aktualisiert den Fortschrittsbalken"""
        self.progress_bar.setValue(value)
    
    def installation_finished(self, success, error_message):
        """Wird aufgerufen, wenn die Installation abgeschlossen ist"""
        if success:
            self.update_status("Installation erfolgreich abgeschlossen!")
            self.log("✓ Alle Komponenten wurden erfolgreich installiert.")
        else:
            self.update_status(f"Installation mit Fehlern abgeschlossen: {error_message}")
            self.log(f"✗ Fehler bei der Installation: {error_message}")
        
        self.cancel_button.setEnabled(False)
        self.completeChanged.emit()
    
    def isComplete(self):
        """Prüft, ob die Seite vollständig ist (Installation abgeschlossen)"""
        if not self.install_thread:
            return False
        return not self.install_thread.isRunning()
    
    def cancel_installation(self):
        """Bricht die Installation ab"""
        if self.install_thread and self.install_thread.isRunning():
            reply = QMessageBox.question(
                self, "Installation abbrechen", 
                "Möchten Sie die Installation wirklich abbrechen?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.update_status("Installation wird abgebrochen...")
                self.install_thread.cancel()
                # Der Thread wird seine finished-Signal auslösen, wenn er sauber beendet wurde


class CompletionPage(QWizardPage):
    """Abschlussseite des Installationsassistenten"""
    def __init__(self):
        super().__init__()
        self.setTitle("Installation abgeschlossen")
        self.setSubTitle("Der VMware vSphere Reporter wurde erfolgreich installiert")
        
        layout = QVBoxLayout()
        
        # Erfolgsmeldung
        success_label = QLabel(
            "<p>Herzlichen Glückwunsch! Der VMware vSphere Reporter wurde erfolgreich auf Ihrem System installiert.</p>"
        )
        success_label.setWordWrap(True)
        success_label.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-size: 12pt; font-weight: bold;")
        layout.addWidget(success_label)
        
        details_label = QLabel(
            "<p>Sie können die Anwendung jetzt über die erstellte Desktop-Verknüpfung oder "
            "direkt aus dem Installationsverzeichnis starten.</p>"
        )
        details_label.setWordWrap(True)
        layout.addWidget(details_label)
        
        layout.addSpacing(20)
        
        # Optionen für den Start
        options_group = QGroupBox("Nach der Installation")
        options_layout = QVBoxLayout()
        
        self.start_now = QCheckBox("VMware vSphere Reporter jetzt starten")
        self.start_now.setChecked(True)
        options_layout.addWidget(self.start_now)
        
        self.open_readme = QCheckBox("README-Datei öffnen")
        options_layout.addWidget(self.open_readme)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Hinweise
        notes_label = QLabel(
            "<p><b>Hinweis:</b> Sollten Sie auf Probleme stoßen, prüfen Sie bitte die Dokumentation "
            "im 'docs'-Verzeichnis oder wenden Sie sich an Ihren Bechtle-Ansprechpartner.</p>"
        )
        notes_label.setWordWrap(True)
        notes_label.setStyleSheet(f"color: {BECHTLE_DARK_GRAY}; font-style: italic;")
        layout.addWidget(notes_label)
        
        layout.addStretch()
        
        # Danke und Copyright
        thank_you = QLabel("Vielen Dank, dass Sie sich für Bechtle entschieden haben!")
        thank_you.setAlignment(Qt.AlignCenter)
        thank_you.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-weight: bold;")
        layout.addWidget(thank_you)
        
        copyright_label = QLabel("© 2025 Bechtle GmbH")
        copyright_label.setAlignment(Qt.AlignRight)
        copyright_label.setStyleSheet(f"color: {BECHTLE_DARK_GRAY}; font-size: 9pt;")
        layout.addWidget(copyright_label)
        
        self.setLayout(layout)
        
        # Registriere Felder
        self.registerField("start_now", self.start_now)
        self.registerField("open_readme", self.open_readme)


class InstallerWizard(QWizard):
    """Hauptklasse des Installationsassistenten"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("VMware vSphere Reporter - Installation")
        
        # Finde Logo-Pfad
        self.logo_path = self._find_logo_path()
        
        if self.logo_path:
            self.setWindowIcon(QIcon(self.logo_path))
        
        # Füge Seiten hinzu
        self.addPage(WelcomePage(self.logo_path))
        self.addPage(PythonDetectionPage())
        self.addPage(InstallationPathPage())
        self.addPage(InstallationPage())
        self.addPage(CompletionPage())
        
        # Setze Layout-Eigenschaften
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.HaveHelpButton, False)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.NoBackButtonOnLastPage, True)
        
        # Stylesheets für Bechtle-Design
        self._apply_bechtle_style()
        
        # Fenstergröße
        self.resize(700, 600)
    
    def _find_logo_path(self):
        """Sucht nach dem Bechtle-Logo"""
        # Verschiedene mögliche Positionen für das Logo
        possible_paths = [
            os.path.join("images", "logo_bechtle.png"),
            os.path.join(os.path.dirname(__file__), "images", "logo_bechtle.png"),
            os.path.join("attached_assets", "logo_bechtle.png"),
            os.path.join(os.path.dirname(__file__), "attached_assets", "logo_bechtle.png"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return None
    
    def _apply_bechtle_style(self):
        """Wendet das Bechtle-Farbschema auf den gesamten Assistenten an"""
        self.setStyleSheet(f"""
            QWizard {{
                background-color: white;
            }}
            QWizardPage {{
                background-color: white;
            }}
            QLabel#MessageLabel {{
                color: {BECHTLE_DARK_BLUE};
            }}
            QPushButton {{
                padding: 5px 15px;
                border: 1px solid {BECHTLE_DARK_GRAY};
                border-radius: 3px;
                background-color: {BECHTLE_LIGHT_GRAY};
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton#nextButton, QPushButton#finishButton {{
                background-color: {BECHTLE_DARK_BLUE};
                color: white;
                font-weight: bold;
            }}
            QProgressBar {{
                border: 1px solid {BECHTLE_DARK_GRAY};
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {BECHTLE_GREEN};
            }}
            QGroupBox {{
                border: 1px solid {BECHTLE_LIGHT_GRAY};
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {BECHTLE_DARK_BLUE};
            }}
        """)
    
    def done(self, result):
        """Wird aufgerufen, wenn der Assistent beendet wird"""
        if result == QWizard.Accepted:
            # Optionen nach der Installation
            if self.field("start_now"):
                self._start_application()
                
            if self.field("open_readme"):
                self._open_readme()
        
        super().done(result)
    
    def _start_application(self):
        """Startet die Anwendung nach der Installation"""
        try:
            install_path = self.field("install_path")
            python_exec = self.field("python_executable")
            app_script = os.path.join(install_path, "vsphere_reporter.py")
            
            if not os.path.exists(app_script):
                logger.error(f"Anwendungsdatei nicht gefunden: {app_script}")
                return
                
            if platform.system() == "Windows":
                # Für Windows starten wir im Hintergrund
                subprocess.Popen(
                    [python_exec, app_script],
                    cwd=install_path,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Für Linux/macOS
                subprocess.Popen(
                    [python_exec, app_script],
                    cwd=install_path
                )
                
            logger.info("Anwendung wurde gestartet")
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Anwendung: {str(e)}")
    
    def _open_readme(self):
        """Öffnet die README-Datei"""
        try:
            install_path = self.field("install_path")
            readme_path = os.path.join(install_path, "README.md")
            
            if os.path.exists(readme_path):
                if platform.system() == "Windows":
                    os.startfile(readme_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", readme_path])
                else:  # Linux
                    subprocess.Popen(["xdg-open", readme_path])
            else:
                logger.warning(f"README-Datei nicht gefunden: {readme_path}")
                
        except Exception as e:
            logger.error(f"Fehler beim Öffnen der README-Datei: {str(e)}")


if __name__ == "__main__":
    # Starte den Installationsassistenten
    app = QApplication(sys.argv)
    wizard = InstallerWizard()
    wizard.show()
    sys.exit(app.exec_())