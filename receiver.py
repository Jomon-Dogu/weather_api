import time

while True:
    try:
        with open("output.txt", "r") as file:
            data = file.read()
            if data == "1":
                print("Empfangen: 1")
                # Weiterverarbeitung hier
                break  # Falls das Skript danach enden soll
    except FileNotFoundError:
        pass
    
    time.sleep(1)  # Wartezeit, um die Datei periodisch zu überprüfen
