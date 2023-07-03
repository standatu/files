import streamlit as st
import sqlite3

class Pojisteny:
    def __init__(self, jmeno, prijmeni, vek, telefon):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.vek = vek
        self.telefon = telefon

    def __str__(self):
        return f'{self.jmeno}, {self.prijmeni}, {self.vek}, {self.telefon}'

class EvidencePojistek:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = '''CREATE TABLE IF NOT EXISTS pojisteni (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jmeno TEXT,
                    prijmeni TEXT,
                    vek INTEGER,
                    telefon TEXT
                )'''
        self.conn.execute(query)

    def pridat_pojisteneho(self, jmeno, prijmeni, vek, telefon):
        query = "INSERT INTO pojisteni (jmeno, prijmeni, vek, telefon) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (jmeno, prijmeni, vek, telefon))
        self.conn.commit()

    def seznam_pojistenych(self):
        query = "SELECT * FROM pojisteni"
        cursor = self.conn.execute(query)
        seznam = []
        for row in cursor:
            pojisteny = Pojisteny(row[1], row[2], row[3], row[4])
            seznam.append(str(pojisteny))
        return seznam

    def fulltext_vyhledavani(self, hledany_vyraz):
        query = "SELECT * FROM pojisteni WHERE jmeno LIKE ? OR prijmeni LIKE ? OR telefon LIKE ?"
        cursor = self.conn.execute(query, (f"%{hledany_vyraz}%", f"%{hledany_vyraz}%", f"%{hledany_vyraz}%"))
        seznam = []
        for row in cursor:
            pojisteny = Pojisteny(row[1], row[2], row[3], row[4])
            seznam.append(str(pojisteny))
        return seznam

db_name = "pojisteni.db"
evidence = EvidencePojistek(db_name)

st.title("Evidence pojistek")

menu = st.sidebar.selectbox("Menu", ["Seznam pojistěných", "Přidat pojištěnce", "Vyhledávání"])

if menu == "Seznam pojistěných":
    seznam = evidence.seznam_pojistenych()
    for pojisteny in seznam:
        st.write(pojisteny)

elif menu == "Přidat pojištěnce":
    with st.form(key='pojisteny_form'):
        st.header("Prosím vyplňte všechny údaje")
        jmeno = st.text_input("Jméno")
        prijmeni = st.text_input("Příjmení")
        vek = st.text_input("Věk")
        telefon = st.text_input("Telefon")
        submitted = st.form_submit_button("Submit")
    
    if submitted:
        if jmeno and prijmeni and vek and telefon:
            evidence.pridat_pojisteneho(jmeno, prijmeni, vek, telefon)
            st.write(f"Pojistěnec {jmeno} byl přidán.")
        else:
            st.error("Please fill in all fields")

elif menu == "Vyhledávání":
    with st.form(key='vyhledavani_form'): 
        hledany_vyraz = st.text_input("Hledaný výraz")
        if st.form_submit_button("Hledat"):
            vysledky = evidence.fulltext_vyhledavani(hledany_vyraz)
            if len(vysledky) > 0:
                for vysledek in vysledky:
                    st.write(vysledek)
            else:
                st.write("Žádný pojištěný nebyl nalezen.")
