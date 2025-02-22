#!/bin/bash
cd /home/pedro/StefanCryptoTradingBot
source /home/pedro/StefanCryptoTradingBot/venv/bin/activate
exec gunicorn -c /home/pedro/StefanCryptoTradingBot/gunicorn_config.py wsgi:app
