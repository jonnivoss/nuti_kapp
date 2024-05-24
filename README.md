# Nutikapp_Lapikutega
Nutikapi kood koostöös Lapikutega.

Kasutajaliidese kood:
I2C ühenduse loomiseks kasutasime SMBus teeki (https://raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2) ning kasutajaliidese visuaalseks kuvamiseks kasutasime guizero (https://lawsie.github.io/guizero/) teeki. 

Programmi alguses luuakse StorageBoxes objekt, mis sisaldab kõigi teisi meetodeid, mida programm kasutab. Et meetodid oleksid rohkem organiseeritud, siis loogikaga ja i2c tegelevad meetodid ehk backend on Storagebox klassis.

Kasutaja liidese klass sisaldab visuallset osa mida klient näeb ja kus ta saab sisestada pin koodi. Koodi sisestuseks oleme kasutanud TextBox objekti.

Kasutajaliidesel on numbri nupud 0-st 9-ni, millega saab sisestada 6-kohalist koodi. Samuti on kasutajaliidesel kustutamise nupp “DEL”, millega saab kõik numbrid tekstiväljas ära kustutada ja uuesti proovida numbreid sisestada. Viimaseks on koodi sisestamise nupp “ENT”, mida vajutades tehakse kapp lahti, kui on õige kood või kuvatakse administraatori paneeli, kui on sisestatud spetsiaalne administraatori kood (1337). Vale koodi korral kuvatakse veateade.

Loodud App objekti full_screen omadus on sätitud tõeseks, kuna siis ei ole võimalik tavakasutajal ligi pääseda operatsioonisüsteemi keskkonnale kasutades puutetundlikku ekraani. Tehnikutel on võimalus väljuda kasutajaliidese programmist kasutades sisestades nutikapi juures spetsiaalset väljumiskoodi (0000).

Vajutades nuppe, kus on peal number, kutsutakse välja add_digit funktsioon, mis lisab numbri tekstiväljale kasutades sõne append meetodit. 

Kustutamise nuppu “DEL” vajutades, kutsutakse välja clear_pin funktsioon, mis kustutab kõik väärtused tekstiväljalt kasutades tühja sõne TextBoxi panemist. 

Koodi sisestamise nuppu “ENT” vajutades, kutsutakse välja funktsioon nimega try_unlock, mis sutsub välja StorageBoxes meetodi check_code, kui kood on olemas avatakse kapp, kui on sisestatud väljumiskood, siis programm läheb kinni ja kui on administraatori kood, siis kuvatakse administraatori paneel.

Administraatori paneel kuvatakse Window vidinaga ja paneel näitab olemasolevaid kappe. Kappe saab avada vajutades soovitud kapi nuppu ning lisaks on võimalik kapile kood genereerida. Koode genereeritakse juhuslikult ja koodid on 6-kohalised. (000000 - 999999)

Installeerimine:

1) Python/Pip - sudo apt install python3 python3-pip
2) I2C - sudo raspi-config -> Interfacing Options -> Enable I2C
3) I2C Tools - sudo apt install -y i2c-tools
4) SMBus - sudo apt install -y python3-smbus
5) guizero - pip3 install guizero

I2C seadmete tuvastamiseks: sudo i2cdetect -y 1

Käivitamine:

1) Ava terminal
2) Navigeeri skripti asukohta (ls - näha faile ja kaustasi, cd <kausta_nimi> - liikuta valitud kausta)
3) python3 <faili_nimi> (nt: python3 nutikapp.py)