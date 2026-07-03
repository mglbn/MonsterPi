#!/bin/bash

systemctl stop monsterpi.service
rm -rf /opt/MonsterPiMonsterPi/src
cp -R "/home/$SUDO_USER/MonsterPi/src" /opt/MonsterPi/src
chown -R kiosk:kiosk /opt/MonsterPi
systemctl start monsterpi.service