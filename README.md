# BankID Indikator (BIDI)

[![flake8 Lint](https://github.com/kragebein/bankid/actions/workflows/flake8_lint.yml/badge.svg)](https://github.com/kragebein/bankid/actions/workflows/flake8_lint.yml)[![Deploy](https://github.com/kragebein/bankid/actions/workflows/deploy.yml/badge.svg)](https://github.com/kragebein/bankid/actions/workflows/deploy.yml)

BankID Indikator viser BankID-status fra nettsidene til bankid.no

De offentlige api-rutene til bankid inkluderer _ikke_ informasjon om en mobiloperatør har problemer med sine nettverk, bankid.no viser derimot denne informasjonen _gratis_.

# Beta

Bidi kan anses for å være beta, og kjører live akkurat nå på https://bankid.lazywack.no i debug modus.

# Hva gjør den egentlig?

BIDI scraper nettsidene til bankid.no og publiserer selv en veldig enkel indikator som kan integrereres på nettsider i påloggingsbilde eller på andre statusoversiktssider.

![eksempel](https://i.postimg.cc/fy56zW5p/image.png)

Fargen på denne sirkelen indikerer hva slags problemer som oppleves:

- Grønn - Alt er ok
- Gul - Tregheter med systemer
- Oransje - En eller flere tjenester er nede hos bankid eller underleverandører.
- Rød - BankID er utilgjengelig.
- Blå - Vedlikehold

Det fins også en egendefinert status:

- Sort - Feil i BIDI, enten forandringer på nettsidene hos bankid.no eller så er BIDI nyoppstartet.

Hvis status er noe annet enn grønn eller sort, kan man holde musen over "dotten" for mer detaljert beskrivelse av hva som er feil.

# Bruk

1.  `git clone http://github.com/kragebein/bankid.git`
2.  `pip3 install -r requirements.txt`
3.  `cd bankid/`
4.  `python3 main.py`

Det startes da opp en webserver på http://0.0.0.0:8080 (med mindre annet konfigurert) som viser statusen på bankid

# Hvorfor

Bidi ble skrevet som et prosjekt for forrige arbeidsgiver hvor vi var avhengige av å vite status på bankid til enhver tid, vi brukte også confluence til enhver tid, så da passet det fint med en indikator i margen.

Så lenge mobiloperatørstatus ikke blir inkludert i APIene vil BIDI fortsette å bruke `requests` og `BeautifulSoup4`.

# Teknisk

Bidi innhenter data fra bankid.no maks en gang hvert 30 sekund.
Oppdaterer du nettsidene en gang hvert sekund, vil ikke statusen oppdatere seg før det har gått 30.

Bruker du ikke nettsidene, vil ikke Bidi hente informasjon før den blir oppdatert.

Rent praktisk kan det være greit med iframe og refresh hvert 15/30 sekund for jevn strøm av data.
