#!/bin/bash         

if [ ! -d "venv" ]; then
  echo -e "No venv found, creating one\n"
  python -m venv venv
  echo -e "Activating venv\n"
  source venv/bin/activate
  echo -e "Installing requirements\n"
  pip install -r frontend/requirements.txt
  pip install -r backend/requirements.txt
else
  echo -e "Activating venv\n"
  source venv/bin/activate
fi
echo -e "Starting application\n"
python frontend/frontend.py
echo -e "Deactivating venv\n"
deactivate