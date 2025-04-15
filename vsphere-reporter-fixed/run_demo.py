#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Demo-Server
Vereinfachte Demo ohne GUI mit direkter HTML-Anzeige
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import time

PORT = 5001

# Erstelle eine Demo-HTML-Datei im Bechtle-Design
BECHTLE_BLUE = "#00355e"
BECHTLE_ORANGE = "#da6f1e"
BECHTLE_GREEN = "#23a96a"

def create_demo_html():
    """Generiert eine Demo-HTML-Datei für den vSphere Reporter v25.2"""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>VMware vSphere Reporter v25.2 - Demo</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        .header {{
            background-color: {BECHTLE_BLUE};
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .feature {{
            background-color: #f5f5f5;
            border-left: 5px solid {BECHTLE_ORANGE};
            padding: 15px;
            margin-bottom: 15px;
        }}
        .nav-fixed {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: {BECHTLE_BLUE};
            color: white;
            display: flex;
            align-items: center;
            padding: 0 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 9999;
        }}
        .nav-title {{
            font-size: 18px;
            font-weight: bold;
            flex: 1;
        }}
        .nav-links {{
            display: flex;
            list-style-type: none;
            margin: 0;
            padding: 0;
        }}
        .nav-links li {{
            margin: 0 10px;
        }}
        .nav-links a {{
            color: rgba(255, 255, 255, 0.85);
            text-decoration: none;
            padding: 20px 12px;
            display: inline-block;
        }}
        .nav-links a:hover, .nav-links a.active {{
            color: white;
            background-color: rgba(255, 255, 255, 0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: {BECHTLE_BLUE};
            color: white;
            padding: 10px;
            text-align: left;
        }}
        td {{
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f3f3f3;
        }}
        .warning {{
            background-color: #ffffcc;
        }}
        .error {{
            background-color: #ffcccc;
        }}
        .section {{
            margin-top: 40px;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <!-- Navigation Bar Demo -->
    <nav class='nav-fixed'>
        <div class='nav-title'>VMware vSphere Reporter v25.2</div>
        <ul class='nav-links'>
            <li><a href='#overview' class='active'>Übersicht</a></li>
            <li><a href='#vmware-tools'>VMware Tools</a></li>
            <li><a href='#snapshots'>Snapshots</a></li>
            <li><a href='#orphaned-vmdks'>Verwaiste VMDKs</a></li>
        </ul>
    </nav>
    
    <div style='height: 70px;'></div>
    
    <div class='container'>
        <div class='header'>
            <h1>VMware vSphere Reporter</h1>
            <p>Version 25.2 - PowerShell-inspirierte VMDK-Erkennung</p>
        </div>
        
        <section id="overview">
            <h2>Neue Features in Version 25.2</h2>
            
            <div class='feature'>
                <h3>Vollständig überarbeitete VMDK-Erkennung</h3>
                <p>Die Version 25.2 bietet eine komplett neu implementierte Methode zur 
                Erkennung verwaister VMDKs mit PowerShell-inspirierter Methodik.</p>
            </div>
            
            <div class='feature'>
                <h3>PowerShell-inspirierter Ansatz für VMDKs</h3>
                <p>Der neu entwickelte Algorithmus basiert auf dem erfolgreichen PowerShell-Skript
                und nutzt einen VM-zentrierten Ansatz zur Erfassung aller Festplatten.</p>
            </div>
            
            <div class='feature'>
                <h3>Verbesserte Pfadvergleiche</h3>
                <p>Mehrere Pfadnormalisierungen werden für präzisere Ergebnisse beim Vergleich von VMDKs eingesetzt.</p>
            </div>
            
            <div class='feature'>
                <h3>Mehrstufige Vergleichslogik</h3>
                <p>Der erweiterte Erkennungsalgorithmus verwendet mehrere Fallback-Mechanismen und
                unterstützt verschiedene VMDK-Pfadformate für eine maximale Erkennungsrate.</p>
            </div>
        </section>
        
        <section id="vmware-tools" class="section">
            <h2>VMware Tools</h2>
            <p>Sortiert nach ältester Version</p>
            
            <table>
                <tr>
                    <th>VM</th>
                    <th>Version</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>vm-001.example.local</td>
                    <td>10.3.5</td>
                    <td>Veraltet</td>
                </tr>
                <tr>
                    <td>vm-002.example.local</td>
                    <td>10.3.5</td>
                    <td>Veraltet</td>
                </tr>
                <tr>
                    <td>vm-003.example.local</td>
                    <td>10.3.10</td>
                    <td>Wird aktualisiert</td>
                </tr>
                <tr>
                    <td>vm-004.example.local</td>
                    <td>11.0.0</td>
                    <td>OK</td>
                </tr>
                <tr>
                    <td>vm-005.example.local</td>
                    <td>11.0.5</td>
                    <td>OK</td>
                </tr>
                <tr>
                    <td>vm-006.example.local</td>
                    <td>11.1.0</td>
                    <td>OK</td>
                </tr>
                <tr>
                    <td>vm-007.example.local</td>
                    <td>11.2.5</td>
                    <td>OK</td>
                </tr>
            </table>
        </section>
        
        <section id="snapshots" class="section">
            <h2>Snapshots</h2>
            <p>Sortiert nach Alter (älteste zuerst)</p>
            
            <table>
                <tr>
                    <th>VM</th>
                    <th>Name</th>
                    <th>Datum</th>
                    <th>Alter (Tage)</th>
                    <th>Größe (MB)</th>
                </tr>
                <tr class="error">
                    <td>vm-042.example.local</td>
                    <td>Pre-Update-2024-01-15</td>
                    <td>2024-01-15 08:30</td>
                    <td>92</td>
                    <td>45,230</td>
                </tr>
                <tr class="error">
                    <td>vm-021.example.local</td>
                    <td>Backup-Before-Migration</td>
                    <td>2024-02-10 14:45</td>
                    <td>65</td>
                    <td>32,500</td>
                </tr>
                <tr class="warning">
                    <td>vm-018.example.local</td>
                    <td>Config-Backup</td>
                    <td>2024-03-12 11:20</td>
                    <td>35</td>
                    <td>18,750</td>
                </tr>
                <tr class="warning">
                    <td>vm-037.example.local</td>
                    <td>Before-Security-Patch</td>
                    <td>2024-03-20 09:15</td>
                    <td>27</td>
                    <td>8,420</td>
                </tr>
                <tr>
                    <td>vm-051.example.local</td>
                    <td>Test-Environment</td>
                    <td>2024-04-05 15:30</td>
                    <td>11</td>
                    <td>5,280</td>
                </tr>
            </table>
        </section>
        
        <section id="orphaned-vmdks" class="section">
            <h2>Verwaiste VMDK-Dateien</h2>
            <p>Durch PowerShell-inspirierte Erkennung identifiziert</p>
            
            <table>
                <tr>
                    <th>Datastore</th>
                    <th>Pfad</th>
                    <th>Name</th>
                    <th>Größe (MB)</th>
                    <th>Letzte Änderung</th>
                </tr>
                <tr>
                    <td>datastore-2</td>
                    <td>[datastore-2] orphaned/orphaned-disk-1.vmdk</td>
                    <td>orphaned-disk-1.vmdk</td>
                    <td>25,600</td>
                    <td>2023-08-15 10:45</td>
                </tr>
                <tr>
                    <td>datastore-1</td>
                    <td>[datastore-1] orphaned/orphaned-disk-2.vmdk</td>
                    <td>orphaned-disk-2.vmdk</td>
                    <td>51,200</td>
                    <td>2023-09-22 14:30</td>
                </tr>
                <tr>
                    <td>datastore-3</td>
                    <td>[datastore-3] orphaned/orphaned-disk-3.vmdk</td>
                    <td>orphaned-disk-3.vmdk</td>
                    <td>76,800</td>
                    <td>2023-11-05 09:15</td>
                </tr>
                <tr>
                    <td>datastore-2</td>
                    <td>[datastore-2] orphaned/orphaned-disk-4.vmdk</td>
                    <td>orphaned-disk-4.vmdk</td>
                    <td>12,800</td>
                    <td>2024-01-18 11:20</td>
                </tr>
                <tr>
                    <td>datastore-1</td>
                    <td>[datastore-1] orphaned/orphaned-disk-5.vmdk</td>
                    <td>orphaned-disk-5.vmdk</td>
                    <td>38,400</td>
                    <td>2024-02-27 16:45</td>
                </tr>
            </table>
            
            <div class="feature">
                <h3>PowerShell-inspirierte Erkennung</h3>
                <p>Die verbesserte Erkennung basiert auf einem VM-zentrierten Ansatz statt reiner Datastore-Scans.
                Dadurch werden genau die VMDKs identifiziert, die zu keiner VM gehören und keine Template-Dateien sind.</p>
            </div>
        </section>
    </div>
</body>
</html>"""

    with open("demo.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print("Demo-HTML-Datei erstellt")

def run_server(port=PORT):
    """Startet einen HTTP-Server zum Hosten der Demo-Seite"""
    try:
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
            print(f"Demo-Server läuft auf http://localhost:{port}")
            print(f"Öffne Browser mit http://localhost:{port}/demo.html")
            
            # Versuche, den Browser zu öffnen
            try:
                webbrowser.open(f"http://localhost:{port}/demo.html")
            except Exception as e:
                print(f"Warnung: Konnte Browser nicht automatisch öffnen: {e}")
                print(f"Bitte öffnen Sie manuell: http://localhost:{port}/demo.html")
            
            # Server starten
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Port {port} ist bereits belegt. Versuche Port {port+1}")
            run_server(port=port+1)  # Rekursiv mit erhöhtem Port versuchen
        else:
            print(f"Fehler beim Starten des HTTP-Servers: {e}")
    except KeyboardInterrupt:
        print("\nServer wurde beendet")

if __name__ == "__main__":
    print("VMware vSphere Reporter Demo v25.2")
    create_demo_html()
    run_server()