#!/bin/bash

systemctl stop myportfolio
cd pe-portfolio-site-project-fork
git fetch && git reset origin/main --hard
python -m venv python3-virtualenv
source python3-virtualenv/bin/activate
pip install -r requirements.txt
systemctl start myportfolio
systemctl enable myportfolio