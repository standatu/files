import tkinter as tk
import sqlite3

# Třída reprezentující pojištěnce
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

# Třída pro evidenci pojištěnců
class EvidencePojistek:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    # Metoda pro vytvoření tabulek v databázi
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

    # Metoda pro přidání pojištěnce do databáze
    def pridat_pojisteneho(self, jmeno, prijmeni, vek, telefon, typ):
        query = "INSERT INTO pojistenci (jmeno, prijmeni, vek, telefon) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (jmeno, prijmeni, vek, telefon))
        self.conn.commit()
        pojisteny_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        query = "INSERT INTO pojisteni (typ, pojisteny_id) VALUES (?, ?)"
        self.conn.execute(query, (typ, pojisteny_id))
        self.conn.commit()

    # Metoda pro úpravu pojištěnce v databázi
    def upravit_pojisteneho(self, id, jmeno, prijmeni, vek, telefon, typ):
        query = "UPDATE pojistenci SET jmeno = ?, prijmeni = ?, vek = ?, telefon = ? WHERE id = ?"
        self.conn.execute(query, (jmeno, prijmeni, vek, telefon, id))  
        query = "UPDATE pojisteni SET typ = ? WHERE pojisteny_id = ?"
        self.conn.execute(query, (typ, id))
        self.conn.commit()

    # Metoda pro smazání pojištěnce z databáze
    def smazat_pojisteneho(self, id):
        query = "DELETE FROM pojistenci WHERE id = ?"
        self.conn.execute(query, (id,))
        query = "DELETE FROM pojisteni WHERE pojisteny_id = ?"
        self.conn.execute(query, (id,))
        self.conn.commit()

    # Metoda pro získání seznamu všech pojištěnců
    def seznam_pojistenych(self):
        query = "SELECT * FROM pojistenci JOIN pojisteni ON pojistenci.id = pojisteni.pojisteny_id"
        cursor = self.conn.execute(query)
        seznam = []
        for row in cursor:
            pojisteny = Pojisteny(row[0], row[1], row[2], row[3], row[4], row[6])
            seznam.append(pojisteny)
        return seznam

    # Metoda pro fulltextové vyhledávání pojištěnců
    def fulltext_vyhledavani(self, hledany_vyraz):
        query = "SELECT pojistenci.id, pojistenci.jmeno, pojistenci.prijmeni, pojistenci.vek, pojistenci.telefon, pojisteni.typ FROM pojistenci JOIN pojisteni ON pojistenci.id = pojisteni.pojisteny_id WHERE jmeno LIKE ? OR prijmeni LIKE ? OR telefon LIKE ?"
        cursor = self.conn.execute(query, (f"%{hledany_vyraz}%", f"%{hledany_vyraz}%", f"%{hledany_vyraz}%"))
        seznam = []
        for row in cursor:
            pojisteny = Pojisteny(row[0], row[1], row[2], row[3], row[4], row[5])
            seznam.append(pojisteny)
        return seznam

# Funkce pro přidání pojištěnce
def pridat_uzivatele():
    global current_mode
    current_mode = "add"
    registrace_frame.pack()
    vyhledavani_frame.pack_forget()
    editace_frame.pack_forget()

# Funkce pro uložení pojištěnce
def ulozit_uzivatele():
    jmeno = jmeno_entry.get()
    prijmeni = prijmeni_entry.get()
    vek = int(vek_entry.get())
    telefon = telefon_entry.get()
    typ = typ_pojisteni.get()

    if current_mode == "add":
        evidence.pridat_pojisteneho(jmeno, prijmeni, vek, telefon, typ)
        vypis_text.delete(1.0, tk.END)
        vypis_text.insert(tk.END, f"Pojistěnec {jmeno} byl přidán.")
    elif current_mode == "edit":
        id, _, _, _, _, _ = vybrany_pojisteny.get().split(", ")
        evidence.upravit_pojisteneho(id, jmeno, prijmeni, vek, telefon, typ)
        vypis_text.delete(1.0, tk.END)
        vypis_text.insert(tk.END, f"Pojistěnec {jmeno} byl upraven.")

    jmeno_entry.delete(0, tk.END)
    prijmeni_entry.delete(0, tk.END)
    vek_entry.delete(0, tk.END)
    telefon_entry.delete(0, tk.END)
    menu_frame.pack()
    registrace_frame.pack_forget()
    editace_frame.pack_forget()


# Funkce pro zobrazení seznamu pojištěnců
def zobraz_seznam(seznam):
    vypis_text.delete(1.0, tk.END)
    for pojisteny in seznam:
        vypis_text.insert(tk.END, str(pojisteny) + "\n")
    vyhledavani_frame.pack_forget()

# Funkce pro vyhledávání pojištěnců
def vyhledavani(event=None):
    vyhledavani_frame.pack()
    vyhledavani_entry.focus_set()  
    registrace_frame.pack_forget()
    vyhledavani_entry.bind("<Return>", hledat_pojistence)

# Funkce pro hledání pojištěnců
def hledat_pojistence(event=None):
    hledany_vyraz = vyhledavani_entry.get()
    vypis_text.delete(1.0, tk.END)
    vypis_text.insert(tk.END, f"Hledám: {hledany_vyraz}\n")

    vysledky = evidence.fulltext_vyhledavani(hledany_vyraz)
    if len(vysledky) > 0:
        for vysledek in vysledky:
            vypis_text.insert(tk.END, str(vysledek) + "\n")
    else:
        vypis_text.insert(tk.END, "Pojištěný nebyl nalezen")

# Funkce pro editaci pojištěnce
def editace_uzivatele():
    global current_mode
    current_mode = "edit"
    editace_frame.pack()  
    vyhledavani_frame.pack_forget()
    registrace_frame.pack_forget()
    aktualizovat_seznam_pojistencu()
    zobraz_seznam(evidence.seznam_pojistenych())

# Funkce pro načtení údajů pojištěnce
def nacist_uzivatele(*args):
    data = vybrany_pojisteny.get().split(", ")
    if len(data) == 6:
        id, jmeno, prijmeni, vek, telefon, typ = data
    else:
        return
    jmeno_entry.delete(0, tk.END)
    jmeno_entry.insert(0, jmeno)
    prijmeni_entry.delete(0, tk.END)
    prijmeni_entry.insert(0, prijmeni)
    vek_entry.delete(0, tk.END)
    vek_entry.insert(0, vek)
    telefon_entry.delete(0, tk.END)
    telefon_entry.insert(0, telefon)
    typ_pojisteni.set(typ)
    registrace_frame.pack()

# Funkce pro smazání pojištěnce
def smazat_uzivatele():
    id, _, _, _, _, _ = vybrany_pojisteny.get().split(", ")
    evidence.smazat_pojisteneho(id)
    vypis_text.delete(1.0, tk.END)
    vypis_text.insert(tk.END, f"Pojistěnec s ID {id} byl smazán.")
    aktualizovat_seznam_pojistencu()

# Funkce pro aktualizaci seznamu pojištěnců v GUI
def aktualizovat_seznam_pojistencu():
    vybrany_pojisteny_dropdown['menu'].delete(0, 'end')
    seznam_pojistencu = evidence.seznam_pojistenych()
    for pojisteny in seznam_pojistencu:
        vybrany_pojisteny_dropdown['menu'].add_command(label=str(pojisteny), command=tk._setit(vybrany_pojisteny, str(pojisteny)))
    vybrany_pojisteny.trace("w", nacist_uzivatele)

db_name = "pojistenci.db"
evidence = EvidencePojistek(db_name)

root = tk.Tk()
root.title("Evidence pojistek")

# Vytvoření menu a tlačítek
menu_frame = tk.Frame(root)
menu_frame.pack(side=tk.BOTTOM, fill=tk.X)

pridat_button = tk.Button(menu_frame, text="Přidat pojištěnce", command=pridat_uzivatele)
pridat_button.pack()

seznam_button = tk.Button(menu_frame, text="Seznam pojistenců", command=lambda: zobraz_seznam(evidence.seznam_pojistenych()))
seznam_button.pack()

vyhledavani_button = tk.Button(menu_frame, text="Vyhledávání", command=vyhledavani)
vyhledavani_button.pack()

editace_button = tk.Button(menu_frame, text="Upravit pojištěnce", command=editace_uzivatele)
editace_button.pack()

registrace_frame = tk.Frame(root)
vyhledavani_frame = tk.Frame(root)
editace_frame = tk.Frame(root)

vybrany_pojisteny = tk.StringVar(editace_frame)
vybrany_pojisteny.set("")
vybrany_pojisteny_dropdown = tk.OptionMenu(editace_frame, vybrany_pojisteny, "")
vybrany_pojisteny_dropdown.pack()

jmeno_label = tk.Label(registrace_frame, text="Jméno:")
jmeno_label.pack()
jmeno_entry = tk.Entry(registrace_frame)
jmeno_entry.pack()

prijmeni_label = tk.Label(registrace_frame, text="Příjmení:")
prijmeni_label.pack()
prijmeni_entry = tk.Entry(registrace_frame)
prijmeni_entry.pack()

vek_label = tk.Label(registrace_frame, text="Věk:")
vek_label.pack()
vek_entry = tk.Entry(registrace_frame)
vek_entry.pack()

telefon_label = tk.Label(registrace_frame, text="Telefon:")
telefon_label.pack()
telefon_entry = tk.Entry(registrace_frame)
telefon_entry.pack()

typ_pojisteni_label = tk.Label(registrace_frame, text="Typ pojistění:")
typ_pojisteni_label.pack()
typ_pojisteni = tk.StringVar(registrace_frame)
typ_pojisteni.set("Auto")
typ_pojisteni_dropdown = tk.OptionMenu(registrace_frame, typ_pojisteni, "Auto", "Dům", "Úraz")
typ_pojisteni_dropdown.pack()

ulozit_button = tk.Button(registrace_frame, text= "Uložit", command=ulozit_uzivatele)
ulozit_button.pack()

vyhledavani_label = tk.Label(vyhledavani_frame, text="Hledaný výraz:")
vyhledavani_label.pack()

vyhledavani_entry = tk.Entry(vyhledavani_frame)
vyhledavani_entry.pack()
vyhledavani_entry.bind("<Return>", hledat_pojistence)

hledat_button = tk.Button(vyhledavani_frame, text="Hledat", command=hledat_pojistence)
hledat_button.pack()

smazat_button = tk.Button(editace_frame, text="Smazat", command=smazat_uzivatele)
smazat_button.pack()

vypis_text = tk.Text(root)
vypis_text.pack()

# Zobrazení seznamu pojištěnců při spuštění aplikace
zobraz_seznam(evidence.seznam_pojistenych())

root.mainloop()
