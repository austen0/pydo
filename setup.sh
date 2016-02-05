#!/usr/bin/env bash

readonly APP_DIR="$HOME/.pydo"

if [ ! -d "$APP_DIR" ]; then
  mkdir $APP_DIR
fi

cp -f pydo.py README.md LICENSE $APP_DIR
