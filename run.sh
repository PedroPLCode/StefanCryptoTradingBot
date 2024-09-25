#!/bin/bash

[ -d "$HOME/.local/bin" ] && PATH="$HOME/.local/bin:$PATH"
export PATH
export FLASK_ENV=development

source venv/bin/activate
flask run