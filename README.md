# onlinecourse-app
tsoha harjoitustyö

**onlinecourse-app** on opetussovellus, joka mahdollistaa verkkokurssien järjestämisen. Sovelluksessa käyttäjät voivat kirjautua joko opettajina tai opiskelijoina. Opettajat voivat luoda kursseja, lisätä kursseille materiaalia ja tehtäviä sekä seurata opiskelijoiden etenemistä. Opiskelijat voivat liittyä kursseille, opiskella sisältöä ja ratkoa tehtäviä.

## Tämänhetkinen tilanne

### Yleiset toiminnot
- **Käyttäjätilit**: Käyttäjä voi rekisteröityä, kirjautua sisään ja ulos sovelluksesta.
- **Käyttäjäroolit**: Käyttäjä voi olla joko opettaja tai opiskelija. Rooli määrittää sovelluksessa saatavilla olevat toiminnot.

### Opiskelijan toiminnot
- **Kurssien selaaminen ja liittyminen**: Opiskelija voi nähdä listan saatavilla olevista kursseista ja liittyä haluamilleen kursseille.
- **Kurssimateriaalin lukeminen**: Opiskelija voi lukea opettajan lisäämiä kurssin tekstimateriaaleja.

### Opettajan toiminnot
- **Kurssien hallinta**: Opettaja voi luoda uuden kurssin, muokata olemassa olevia kursseja.         
- **Materiaalin ja tehtävien lisäys**: Opettaja voi lisätä kurssille tekstimateriaalia.

**Ei vielä toteutettu:**
- **Tehtävien suorittaminen**: Opiskelija voi ratkoa kurssin automaattisesti tarkastettavia tehtäviä.
- **Suoritusstatistiikka**: Opiskelija voi nähdä tilaston siitä, mitkä kurssin tehtävät hän on jo ratkonut.

- **Kurssien poistaminen**: Opettaja voi poistaa luomiaan kursseja
- **Tehtävät**:
  - **Monivalintatehtävät**: Opettaja voi luoda monivalintatehtäviä, joissa opiskelija valitsee oikean vastauksen annetuista vaihtoehdoista.
  - **Avoimet kysymykset**: Opettaja voi luoda tehtäviä, joihin opiskelijan tulee kirjoittaa oikea vastaus tekstikenttään.
- **Opiskelijatilastot**: Opettaja voi nähdä, ketkä opiskelijat ovat liittyneet kurssille ja mitkä tehtävät kukin opiskelija on suorittanut.


## Käynnistysohjeet

Sovellus ei ainakaan toistaiseksi ole testattavissa Fly.iossa, mutta sen saa käynnistettyä paikallisesti seuraavien ohjeiden mukaisesti:

- Kloonaa tämä repositorio GitHubista omalle koneellesi. Siirry projektin juurikansioon, ja luo sinne .env-tiedosto, jonka sisältö määritellään seuraavanlaiseksi:

    SECRET_KEY=<salainen-avain>
    DATABASE_URL=<tietokannan-paikallinen-osoite>

- Aktivoi sovelluksen virtuaaliympäristö seuraavilla komennoilla:

    $ python3 -m venv venv
    $ source venv/bin/activate

- Asenna sovelluksen riippuvuudet:

    $ pip install -r ./requirements.txt

- Määritä sovelluksen käyttämän postgresql-tietokannan skeema:

    $ psql < schema.sql

- Käynnistä sovellus:

    $ flask run



