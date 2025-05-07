#!/bin/bash
# Bechtle vSphere Reporter v0.1 - Intelligenter Starter für Linux
echo "Starte Bechtle vSphere Reporter v0.1 (intelligente Portauswahl)..."

# Virtuelle Umgebung aktivieren, falls vorhanden
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Starte den Python-Starter
python3 start.py