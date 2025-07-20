#!/bin/bash

PASSWD=$(jq -r '.password' server_config.json)
KEY=$(jq -r '.server_key' server_config.json)
NAME=$(jq -r '.name' agent_config.json)

mkdir -p /tmp/$NAME/

cp LinuxScript.sh /tmp/$NAME/
cp main.bin /tmp/$NAME/
cp agent_config.json /tmp/$NAME/

cd /tmp/$NAME

python=$(which python)
$python -m http.server 1337 &

ip=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '^127\.' | head -n1)

sshpass -p "$PASSWD" ssh root@"$KEY" "
	mkdir -p /tmp/$NAME;
	wget http://$ip:1337/main.bin -O /tmp/$NAME/main.bin;
	wget http://$ip:1337/LinuxScript.sh -O /tmp/$NAME/LinuxScript.sh;
	wget http://$ip:1337/agent_config.json -O /tmp/$NAME/agent_config.json;
	chmod +x /tmp/$NAME/main.bin /tmp/$NAME/LinuxScript.sh;
	sudo /tmp/$NAME/LinuxScript.sh;
	rm -rf /tmp/*
"

cd /tmp && rm -rf /tmp/$NAME
pkill -f http.server
