#!/bin/bash

DIR="$(dirname "$0")"
chmod +x "$DIR/nuitkaScript.sh"
chmod +x "$DIR/deploy.sh"

"$DIR/nuitkaScript.sh" && "$DIR/deploy.sh"
