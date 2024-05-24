# Koodi kirjeldus

Koodis on 4 klassi, StorageBoxes, AdminWeb, AdminPanel, CustomerGUI.

koodi käivitamisel tehakse StorageBoxes klassi objekt kus loetakse siise failist hetkel olemas olevad kapid.
siis tehakse AdminWeb klassi objekt mis sisaldab endast veebi liidest, mis asub lokaalses võrgus. Edasi tehakse CustomerGUI klassi objekt,
mis kuvab kasutajale kasutaja paneeli. Kliendi paneelil on 0-9 nupud numbrite sisestamiseks, enter ja delete klahv koodi esitamiseks ja kustutamiseks.
Kood on 6 kohaline ja kui vajutatakse enter, siis kontrollitakse kas see on mingi kapi pin kood, kui leitakse see kapp siis avatakse selle kapi uks.

Kasutaja liidese klassis on olemas meetodid, koodi sisestamiseks, ja kutsumaks StorageBoxes klassi meetodit check_code, mis avab vastava ukse.
