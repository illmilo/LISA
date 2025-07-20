#!/bin/bash

DIR="$(dirname "$0")"

BIN="$DIR/main.bin"
USER_ROOT="root"
CONFIG_PATH="$DIR/agent_config.json"
CONFIG_NAME=$(jq -r '.name' $CONFIG_PATH)
createUser() {
	local name=$CONFIG_NAME
	if id -u "$name" &>/dev/null
	then
	       	sudo userdel -f -r "$name" &>/dev/null
		sudo sed -i "/^DenyUsers.*\b$name\b/d" /etc/ssh/sshd_config
        	sudo sed -i "/^-:$name:ALL/d" /etc/security/access.conf
		sudo rm -f /etc/sudoers.d/$name
	fi
	sudo useradd -m -s /bin/bash "$name"
	sudo usermod -aG audio,video,plugdev "$name"
	echo "DenyUsers $name" | sudo tee -a /etc/ssh/sshd_config >/dev/null
    	echo "-:$name:ALL" | sudo tee -a /etc/security/access.conf >/dev/null
    	sudo systemctl reload sshd
	sudo usermod -aG sudo "$name"
	echo "$name ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$name > /dev/null
	sudo chmod 440 /etc/sudoers.d/$name
	echo "$name"
}
gnome_injection() {
	local name=$CONFIG_NAME
	local binary_path=$BIN
	local uid=$(id -u "$USER_ROOT")
	local dir_home=$(eval echo "~$name")
	
	local command="sudo -u '$name' bash -c 'cd \"$dir_home\" && NO_AT_BRIDGE=1 \"$binary_path\"'"

	sudo -u "$name" bash -c "cd \"$dir_home\" && NO_AT_BRIDGE=1 \"$binary_path\""
}
tempdir=$(mktemp -d)
chmod 755 "$tempdir"

cp "$BIN" "$tempdir/main.bin"

chmod 755 "$tempdir/main.bin"
tempbin="$tempdir/main.bin"


createUser

chmod +x "$tempbin"

gnome_injection
