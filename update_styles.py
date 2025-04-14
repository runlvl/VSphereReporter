#!/usr/bin/env python3

with open('templates/styles.css', 'r') as f:
    content = f.read()

# Füge die zusätzlichen Stile für Navigation und Sprungmarken hinzu
additional_styles = '''
/* Verbesserungen für die Navigation */
.nav-fixed {
    z-index: 9999; /* Stellt sicher, dass die Navigationsleiste immer über allem anderen liegt */
}

.nav-logo-placeholder {
    height: 28px;
    width: 28px;
    background-color: #da6f1e;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 15px;
    border-radius: 4px;
}

/* Verbesserungen für Sprungmarken */
.section-link {
    color: #00355e;
    text-decoration: none;
    font-weight: 500;
    border-bottom: 1px dotted #00355e;
}

.section-link:hover {
    color: #da6f1e;
    border-bottom: 1px solid #da6f1e;
}

/* Anpassungen für die feste Navigationsleiste */
body {
    scroll-padding-top: 70px; /* Wichtig für Ankerlinks mit fester Navigation */
}

.section {
    scroll-margin-top: 70px; /* Alternative für ältere Browser */
}

/* Zusätzliche Stile für verbesserte Sprungmarken */
.data-table tr.clickable {
    cursor: pointer;
}

.data-table tr.clickable:hover {
    background-color: rgba(218, 111, 30, 0.1);
}
'''

# Füge die Stile am Ende der Datei hinzu
if "/* Verbesserungen für die Navigation */" not in content:
    content += "\n" + additional_styles

with open('templates/styles.css', 'w') as f:
    f.write(content)

print("Styles aktualisiert")
