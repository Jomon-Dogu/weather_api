import time

b_found = False

while True:
    output = "a"  # Beispiel für die Ausgabe
    if time.time() % 5 < 1:  # Ändert zu "b" alle paar Sekunden
        output = "b"
    
    print(output)

    if output == "b" and not b_found:
        b_found = True
        with open("output.txt", "w") as file:
            file.write("1")
    
    time.sleep(1)
