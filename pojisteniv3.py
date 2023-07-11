import streamlit as st
import sqlite3

class Pojisteny:
    def __init__(self, id, jmeno, prijmeni, vek, telefon, typ):
        self.id = id
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.vek = vek
        self.telefon = telefon
        self.typ = typ

    def __str__(self):
        return f'{self.id}, {self.jmeno}, {self.prijmeni}, {self.vek}, {self.telefon}, {self.typ}'

class EvidencePojistek:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    # Vytvoření a prace s sql databází
    def create_table(self):
        query = '''CREATE TABLE IF NOT EXISTS pojistenci (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jmeno TEXT,
                    prijmeni TEXT,
                    vek INTEGER,
                    telefon TEXT
                )'''
        self.conn.execute(query)

        query = '''CREATE TABLE IF NOT EXISTS pojisteni (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    typ TEXT,
                    pojisteny_id INTEGER,
                    FOREIGN KEY (pojisteny_id) REFERENCES pojistenci(id)
                )'''
        self.conn.execute(query)

    def pridat_pojisteneho(self, jmeno, prijmeni, vek, telefon, typ):
        query = "INSERT INTO pojistenci (jmeno, prijmeni, vek, telefon) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (jmeno, prijmeni, vek, telefon))
        self.conn.commit()
        pojisteny_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        query = "INSERT INTO pojisteni (typ, pojisteny_id) VALUES (?, ?)"
        self.conn.execute(query, (typ, pojisteny_id))
        self.conn.commit()

    def upravit_pojisteneho(self, id, jmeno, prijmeni, vek, telefon, typ):
        query = "UPDATE pojistenci SET jmeno = ?, prijmeni = ?, vek = ?, telefon = ? WHERE id = ?"
        self.conn.execute(query, (jmeno, prijmeni, vek, telefon, id))  
        query = "UPDATE pojisteni SET typ = ? WHERE pojisteny_id = ?"
        self.conn.execute(query, (typ, id))
        self.conn.commit()

    def smazat_pojisteneho(self, id):
        query = "DELETE FROM pojistenci WHERE id = ?"
        self.conn.execute(query, (id,))
        query = "DELETE FROM pojisteni WHERE pojisteny_id = ?"
        self.conn.execute(query, (id,))
        self.conn.commit()

    def seznam_pojistenych(self):
        query = "SELECT * FROM pojistenci JOIN pojisteni ON pojistenci.id = pojisteni.pojisteny_id"
        cursor = self.conn.execute(query)
        seznam = []
        for row in cursor:
            pojisteny = Pojisteny(row[0], row[1], row[2], row[3], row[4], row[6])
            seznam.append(pojisteny)
        return seznam

    def najit_pojisteneho(self, id):
        query = "SELECT * FROM pojistenci JOIN pojisteni ON pojistenci.id = pojisteni.pojisteny_id WHERE pojistenci.id = ?"
        cursor = self.conn.execute(query, (id,))
        row = cursor.fetchone()
        if row is not None:
            return Pojisteny(row[0], row[1], row[2], row[3], row[4], row[6])
        else:
            return None

    def fulltext_vyhledavani(self, hledany_vyraz):
        query = "SELECT pojistenci.id, pojistenci.jmeno, pojistenci.prijmeni, pojistenci.vek, pojistenci.telefon, pojisteni.typ FROM pojistenci JOIN pojisteni ON pojistenci.id = pojisteni.pojisteny_id WHERE jmeno LIKE ? OR prijmeni LIKE ? OR telefon LIKE ?"
        cursor = self.conn.execute(query, (f"%{hledany_vyraz}%", f"%{hledany_vyraz}%", f"%{hledany_vyraz}%"))
        seznam = []
        for row in cursor:
            pojisteny = Pojisteny(row[0], row[1], row[2], row[3], row[4], row[5])
            seznam.append(pojisteny)
        return seznam

db_name = "pojistenci.db"
evidence = EvidencePojistek(db_name)


st.sidebar.title('Menu')

# Vytvoření formuláře pro přidání 
with st.sidebar.form(key='add_form'):
    st.header('Přidat pojištěnce')
    jmeno = st.text_input(label='Jméno')
    prijmeni = st.text_input(label='Příjmení')
    vek = st.number_input(label='Věk', min_value=0, max_value=100, value=25)
    telefon = st.text_input(label='Telefon')
    typ = st.selectbox('Typ pojistění', ('Auto', 'Dům', 'Úraz'))
    submit_button = st.form_submit_button(label='Přidat pojištěnce')

    if submit_button:
        evidence.pridat_pojisteneho(jmeno, prijmeni, vek, telefon, typ)
        st.write(f"Pojistěnec {jmeno} byl přidán.")

# Vytvoření formuláře pro úpravu 
with st.sidebar.form(key='edit_form'):
    st.header('Upravit pojištěnce')
    id = st.selectbox('Vyberte pojistence', [p.id for p in evidence.seznam_pojistenych()])
    pojisteny = evidence.najit_pojisteneho(id)
    if pojisteny is not None:
        jmeno = st.text_input(label='Jméno', value=pojisteny.jmeno)
        prijmeni = st.text_input(label='Příjmení', value=pojisteny.prijmeni)
        vek = st.number_input(label='Věk', min_value=0, max_value=100, value=pojisteny.vek)
        telefon = st.text_input(label='Telefon', value=pojisteny.telefon)
        typ = st.selectbox('Typ pojistění', ('Auto', 'Dům', 'Úraz'), index=('Auto', 'Dům', 'Úraz').index(pojisteny.typ))
        submit_button = st.form_submit_button(label='Upravit pojištěnce')

        if submit_button:
            evidence.upravit_pojisteneho(id, jmeno, prijmeni, vek, telefon, typ)
            st.write(f"Pojistěnec {jmeno} byl upraven.")

# Vytvoření formuláře pro smazání 
with st.sidebar.form(key='delete_form'):
    st.header('Smazat pojištěnce')
    id = st.number_input(label='ID', min_value=0)
    submit_button = st.form_submit_button(label='Smazat pojištěnce')

    if submit_button:
        evidence.smazat_pojisteneho(id)
        st.write(f"Pojistěnec s ID {id} byl smazán.")

# Vytvoření formuláře pro vyhledávání 
with st.sidebar.form(key='search_form'):
    st.header('Vyhledávání')
    hledany_vyraz = st.text_input(label='Hledaný výraz')
    submit_button = st.form_submit_button(label='Hledat')

    if submit_button:
        vysledky = evidence.fulltext_vyhledavani(hledany_vyraz)
        if len(vysledky) > 0:
            for vysledek in vysledky:
                st.write(str(vysledek))
        else:
            st.write("Pojištěný nebyl nalezen")

# Zobrazení seznamu 
st.header('Seznam pojistenců')
seznam = evidence.seznam_pojistenych()
for pojisteny in seznam:
    st.write(str(pojisteny))