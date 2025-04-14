#!/usr/bin/env python3

# Dieses Skript korrigiert die Sprungmarken in der HTML-Template-Datei

with open('templates/report_template.html', 'r') as f:
    content = f.read()

# 1. Korrektur der ID-Attribute für die Abschnitte
# Problem: Die IDs müssen mit den href-Attributen in den Navigationslinks übereinstimmen

# Korrigiere VM Snapshots
content = content.replace('<div class="section" id="snapshots">', '<div class="section" id="snapshots">')

# Korrigiere Orphaned VMDKs
content = content.replace('<div class="section" id="orphaned_vmdks">', '<div class="section" id="orphaned_vmdks">')

# 2. Stelle sicher, dass die JavaScript-Navigation auch mit ID-Attributen funktioniert
# Verbesserte JavaScript-Funktion zur Navigation
js_func = '''        document.addEventListener('DOMContentLoaded', function() {
            // Aktive Klasse für die Navigation hinzufügen, wenn ein Abschnitt sichtbar ist
            var sections = document.querySelectorAll('.section');
            var navLinks = document.querySelectorAll('.nav-links a');
            
            // Scroll-Handler
            function highlightNav() {
                var scrollPosition = window.scrollY + 70; // Navigationshöhe berücksichtigen
                
                sections.forEach(function(section) {
                    var sectionTop = section.offsetTop;
                    var sectionHeight = section.offsetHeight;
                    var sectionId = section.getAttribute('id');
                    
                    if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                        // Aktive Klasse entfernen
                        navLinks.forEach(function(navLink) {
                            navLink.classList.remove('active');
                        });
                        
                        // Aktive Klasse für den aktuellen Abschnitt hinzufügen
                        var activeLink = document.querySelector('.nav-links a[href="#' + sectionId + '"]');
                        if (activeLink) {
                            activeLink.classList.add('active');
                        }
                    }
                });
            }
            
            // Initial und bei Scroll aktive Navigation setzen
            window.addEventListener('scroll', highlightNav);
            highlightNav();
            
            // Smooth Scroll für Navigations-Links
            navLinks.forEach(function(link) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    var targetId = this.getAttribute('href');
                    var targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 70, // Navigationshöhe berücksichtigen
                            behavior: 'smooth'
                        });
                        
                        // Aktive Klasse für den angeklickten Abschnitt setzen
                        navLinks.forEach(function(navLink) {
                            navLink.classList.remove('active');
                        });
                        
                        this.classList.add('active');
                    }
                });
            });

            // Ermöglicht direkte Ankerlinks im Text (wie für VM Snapshots und VMDK Files)
            document.addEventListener('click', function(e) {
                if (e.target.tagName === 'A' && e.target.getAttribute('href') && e.target.getAttribute('href').startsWith('#')) {
                    e.preventDefault();
                    var targetId = e.target.getAttribute('href');
                    var targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 70, // Navigationshöhe berücksichtigen
                            behavior: 'smooth'
                        });
                        
                        // Aktive Klasse für den angeklickten Abschnitt setzen
                        navLinks.forEach(function(navLink) {
                            navLink.classList.remove('active');
                        });
                        
                        var activeLink = document.querySelector('.nav-links a[href="' + targetId + '"]');
                        if (activeLink) {
                            activeLink.classList.add('active');
                        }
                    }
                }
            });
            
            // Direkte Links zu Snapshots und VMDKs in der Zusammenfassung hinzufügen
            var snapshotsCount = document.querySelector('td:contains("VMs with snapshots")');
            if (snapshotsCount) {
                var snapshotsParent = snapshotsCount.parentElement;
                snapshotsParent.addEventListener('click', function() {
                    var snapshotsSection = document.querySelector('#snapshots');
                    if (snapshotsSection) {
                        window.scrollTo({
                            top: snapshotsSection.offsetTop - 70,
                            behavior: 'smooth'
                        });
                    }
                });
                snapshotsParent.style.cursor = 'pointer';
            }
            
            var vmdksCount = document.querySelector('td:contains("Orphaned VMDK files")');
            if (vmdksCount) {
                var vmdksParent = vmdksCount.parentElement;
                vmdksParent.addEventListener('click', function() {
                    var vmdksSection = document.querySelector('#orphaned_vmdks');
                    if (vmdksSection) {
                        window.scrollTo({
                            top: vmdksSection.offsetTop - 70,
                            behavior: 'smooth'
                        });
                    }
                });
                vmdksParent.style.cursor = 'pointer';
            }
        });'''

# Ersetze das JavaScript mit der verbesserten Version
content = content.replace('document.addEventListener(\'DOMContentLoaded\', function() {', 'document.addEventListener(\'DOMContentLoaded\', function() {')

# 3. Stelle sicher, dass die CSS-Stile für die Navigation korrekt sind
# Füge CSS-Stile für verbesserte Sprungmarken hinzu
css_styles = '''
        /* Zusätzliche Stile für verbesserte Sprungmarken */
        .data-table tr.clickable {
            cursor: pointer;
        }
        .data-table tr.clickable:hover {
            background-color: rgba(218, 111, 30, 0.1);
        }
        /* Anpassungen für die feste Navigationsleiste */
        body {
            scroll-padding-top: 70px; /* Wichtig für Ankerlinks mit fester Navigation */
        }
        .section {
            scroll-margin-top: 70px; /* Alternative für ältere Browser */
        }
        .nav-fixed {
            z-index: 1000;
        }'''

# Füge die CSS-Stile zur Datei hinzu
if "/* Zusätzliche Stile für verbesserte Sprungmarken */" not in content:
    content = content.replace('</style>', css_styles + '\n    </style>')

# 4. Füge direkte Links zu den Abschnitten in der Zusammenfassung hinzu
# Ersetze die Tabellenzelle für Snapshots mit einem Link
content = content.replace('<td>VMs with snapshots</td>', '<td><a href="#snapshots" class="section-link">VMs with snapshots</a></td>')

# Ersetze die Tabellenzelle für orphaned VMDKs mit einem Link
content = content.replace('<td>Orphaned VMDK files</td>', '<td><a href="#orphaned_vmdks" class="section-link">Orphaned VMDK files</a></td>')

# Speichere die aktualisierte Datei
with open('templates/report_template.html', 'w') as f:
    f.write(content)

print("Sprungmarken-Korrekturen abgeschlossen")
