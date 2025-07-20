#!/bin/bash
FLAGS=(
	--standalone
	--onefile
	--include-data-files=agent_config.json=agent_config.json
)
python3 -m nuitka "${FLAGS[@]}" "main.py"
if [ $? -eq 0 ]; then
	echo -e "Compiled!"
else
	echo -e "Error!"
fi
