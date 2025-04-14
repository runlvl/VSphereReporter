#!/usr/bin/env python3

with open('templates/report_template.html', 'r') as f:
    content = f.read()

# Ersetze das Logo im Kopf der Seite
updated_content = content.replace('''            <!-- Bechtle Logo (PNG) -->
            <img src="data:image/png;base64,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" alt="Bechtle Logo" class="logo">''', '''            <!-- Bechtle Logo (PNG) -->
            {% if bechtle_logo %}
            <img src="data:image/png;base64,{{ bechtle_logo }}" alt="Bechtle Logo" class="logo">
            {% else %}
            <div class="logo-placeholder">Bechtle Logo</div>
            {% endif %}''')

with open('templates/report_template.html', 'w') as f:
    f.write(updated_content)

print("Logo-Ersetzung abgeschlossen")
