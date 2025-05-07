#!/bin/bash
echo "Starte Bechtle vSphere Reporter v0.1..."
export PYTHONWARNINGS=ignore
export FLASK_ENV=production
export FLASK_APP=app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000

# Starte Browser (je nach Desktop-Umgebung)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000 &
elif command -v gnome-open > /dev/null; then
    gnome-open http://localhost:5000 &
elif command -v open > /dev/null; then
    open http://localhost:5000 &
fi

python3 app.py