#!/bin/bash

# Endlosschleife zur Überprüfung des Datei-Inhalts
while true; do
    # Überprüfen, ob die Datei existiert
    if [[ -f "output.txt" ]]; then
        # Inhalt der Datei lesen
        data=$(cat output.txt)

        # Überprüfen, ob der Inhalt "1" ist
        if [[ "$data" == "1" ]]; then
            echo "21,1" > /proc/lll-gpio
            # Hier könnte eine weitere Verarbeitung erfolgen

            break  # Schleife beenden, falls das Skript danach enden soll
        else
                echo "21,0" > /proc/lll-gpio
        fi
    else

                echo "Datei output.txt nicht gefunden"
    fi

    # Warte 1 Sekunde, bevor die Datei erneut überprüft wird
    sleep 1
done
