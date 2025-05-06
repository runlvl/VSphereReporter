#!/bin/bash
echo "Starte VMware vSphere Reporter v18 (Diagnose-Version)..."
echo

export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONPATH=$(pwd)
export VSPHERE_REPORTER_DEBUG=1

python -m flask run --host=0.0.0.0 --port=5000