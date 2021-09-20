#!/bin/bash

#############################
# Create DMG
#############################

if [[ $GITHUB_REF == refs/heads/* ]] ;
then
    VERSION=${GITHUB_REF#refs/heads/}
else
	if [[ $GITHUB_REF == refs/tags/* ]] ;
	then
		VERSION=${GITHUB_REF#refs/tags/}
	else
		exit 1
	fi
fi

rm lightcycler*dmg

LIGHTCYCLER_DMG=lightcycler-${VERSION}-macOS-amd64.dmg
hdiutil unmount /Volumes/lightcycler -force -quiet
sleep 5
./deploy/macos/create-dmg --background "./deploy/macos/resources/dmg/dmg_background.jpg" \
                                                     --volname "lightcycler" \
									             	 --window-pos 200 120 \
										 			 --window-size 800 400 \
										 			 --icon lightcycler.app 200 190 \
										 			 --hide-extension lightcycler.app \
										 			 --app-drop-link 600 185 \
										 			 "${LIGHTCYCLER_DMG}" \
										 			 ./dist
