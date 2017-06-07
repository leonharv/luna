#!/usr/bin/env bash

POST_SCRIPT=$1

sleep 10

while [ true ]; do
        status="$(pidof moonlight | wc -w)"
        if [ ${status} -ne 1 ]; then
            if [ ${POST_SCRIPT} != "" ]; then
                ${POST_SCRIPT}
            fi

						if [ -f /lib/systemd/system/kodi.service ] || [ -f /etc/systemd/system/kodi.service ]; then
							sudo systemctl restart kodi &
						else
							sudo systemctl restart mediacenter &
						fi
            exit
        else
            sleep 2
        fi
done
