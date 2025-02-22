#!/bin/bash
cd /home/pedro/StefanCryptoTradingBot
source venv/bin/activate
gunicorn -c gunicorn_config.py wsgi:app

