# onlinecourse-app
tsoha harjoitustyö

**onlinecourse-app** on opetussovellus, joka mahdollistaa verkkokurssien järjestämisen. Sovelluksessa käyttäjät voivat kirjautua joko opettajina tai opiskelijoina. Opettajat voivat luoda kursseja, lisätä kursseille materiaalia ja tehtäviä sekä seurata opiskelijoiden etenemistä. Opiskelijat voivat liittyä kursseille, opiskella sisältöä ja ratkoa tehtäviä.


## Sovelluksen toiminnot

### Yleiset toiminnot
- **Käyttäjätilit**: Käyttäjä voi rekisteröityä, kirjautua sisään ja ulos sovelluksesta.
- **Käyttäjäroolit**: Käyttäjä voi olla joko opettaja tai opiskelija. Rooli määrittää sovelluksessa saatavilla olevat toiminnot.

### Opiskelijan toiminnot
- **Kurssien selaaminen ja liittyminen**: Opiskelija voi nähdä listan saatavilla olevista kursseista ja liittyä haluamilleen kursseille.
- **Kurssimateriaalin lukeminen**: Opiskelija voi lukea opettajan lisäämiä kurssin tekstimateriaaleja.
- **Tehtävien suorittaminen**: Opiskelija voi ratkoa kurssin monivalintatehtäviä, sekä tehtäviä, joissa kirjoitetaan vastaus tekstikenttään.
- **Suoritusstatistiikka**: Opiskelija voi nähdä tilaston siitä, mitkä kurssin tehtävät hän on jo ratkonut.

### Opettajan toiminnot
- **Kurssien hallinta**: Opettaja voi luoda uuden kurssin, muokata olemassa olevia kursseja.         
- **Kurssien poistaminen**: Opettaja voi poistaa luomiaan kursseja
- **Materiaalin ja tehtävien lisäys**: Opettaja voi lisätä kurssille tekstimateriaalia.
- **Tehtävät**:
  - **Avoimet kysymykset**: Opettaja voi luoda tehtäviä, joihin opiskelijan tulee kirjoittaa oikea vastaus tekstikenttään.
  - **Monivalintatehtävät**: Opettaja voi luoda monivalintatehtäviä, joissa opiskelija valitsee oikean vastauksen annetuista vaihtoehdoista.
- **Opiskelijatilastot**: Opettaja voi nähdä, ketkä opiskelijat ovat liittyneet kurssille ja mitkä tehtävät kukin opiskelija on suorittanut.


## Tekninen toteutus

### Sovellus on toteutettu seuraavilla teknologioilla:

- **Backend**: Python (Flask-web-framework)
- **Frontend**: HTML, CSS
- **Tietokanta**: PostgreSQL

PostgreSQL-tietokanta sisältää kaikki sovelluksen tietorakenteet, kuten käyttäjät, kurssit, tehtävät ja suoritustiedot.
HTML/CSS-pohjaiset käyttöliittymäsivut renderöidään Flaskin avulla.
Flask vastaa reittien määrittelystä ja liikenteen hallinnasta käyttäjän ja tietokannan välillä.


## Käynnistysohjeet

Sovelluksen saa käynnistettyä paikallisesti seuraavien ohjeiden mukaisesti:

1. **Kloonaa tämä repositorio** GitHubista omalle koneellesi. Siirry projektin juurikansioon, ja luo sinne `.env`-tiedosto, jonka sisältö määritellään seuraavanlaiseksi:

    ```
    SECRET_KEY=<salainen-avain>
    DATABASE_URL=<tietokannan-paikallinen-osoite>
    ```

2. **Aktivoi sovelluksen virtuaaliympäristö** seuraavilla komennoilla:

    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```

3. **Asenna sovelluksen riippuvuudet**:

    ```bash
    $ pip install -r ./requirements.txt
    ```

4. **Määritä sovelluksen käyttämän PostgreSQL-tietokannan skeema**:

    ```bash
    $ psql < schema.sql
    ```

5. **Käynnistä sovellus**:

    ```bash
    $ flask run
    ```



