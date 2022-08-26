# BankID Indikator (BIDI)

[![flake8 Lint](https://github.com/kragebein/bankid/actions/workflows/flake8_lint.yml/badge.svg)](https://github.com/kragebein/bankid/actions/workflows/flake8_lint.yml)

BankID Indikator viser BankID-status fra nettsidene til bankid.no

De offentlige api-rutene til bankid inkluderer _ikke_ informasjon om en mobiloperatør har problemer med sine nettverk, bankid.no viser derimot denne informasjonen _gratis_.

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
I tillegg lagrer den status for hver time som går, og viser dette i en linke under selve indkatoren som gir en historikk på en uke bak i tid. 

# Python

1.  `git clone http://github.com/kragebein/bankid.git`
2.  `pip3 install -r requirements.txt`
3.  `cd bankid/`
4.  `python3 main.py`

Det startes da opp en webserver på http://0.0.0.0:8080 (med mindre annet konfigurert) som viser statusen på bankid

# Docker

1. `docker build -t bankid .`
2. `docker run -d -p 8080:8080 --network=host --name bankid bankid`
