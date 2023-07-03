import tkinter as tk
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


def pridat_uzivatele():
    registrace_frame.pack()
    vyhledavani_frame.pack_forget()


def ulozit_uzivatele():
    jmeno = jmeno_entry.get()
    prijmeni = prijmeni_entry.get()
    vek = int(vek_entry.get())
    telefon = telefon_entry.get()
    evidence.pridat_pojisteneho(jmeno, prijmeni, vek, telefon)
    vypis_text.delete(1.0, tk.END)
    vypis_text.insert(tk.END, f"Pojistěnec {jmeno} byl přidán.")
    jmeno_entry.delete(0, tk.END)
    prijmeni_entry.delete(0, tk.END)
    vek_entry.delete(0, tk.END)
    telefon_entry.delete(0, tk.END)
    menu_frame.pack()
    registrace_frame.pack_forget()
    vyhledavani_frame.pack_forget()


def zobraz_seznam_pojistenych():
    vypis_text.delete(1.0, tk.END)
    seznam = evidence.seznam_pojistenych()
    for pojisteny in seznam:
        vypis_text.insert(tk.END, pojisteny + "\n")
    vyhledavani_frame.pack_forget()


def vyhledavani(event=None):
    vyhledavani_frame.pack()
    vyhledavani_entry.focus_set()  
    registrace_frame.pack_forget()

    
    vyhledavani_entry.bind("<Return>", hledat_pojistence)


def hledat_pojistence(event=None):
    hledany_vyraz = vyhledavani_entry.get()
    vypis_text.delete(1.0, tk.END)
    vypis_text.insert(tk.END, f"Hledám: {hledany_vyraz}\n")

    vysledky = evidence.fulltext_vyhledavani(hledany_vyraz)
    if len(vysledky) > 0:
        for vysledek in vysledky:
            vypis_text.insert(tk.END, vysledek + "\n")
    else:
        vypis_text.insert(tk.END, "Pojištěný nebyl nalezen")


db_name = "pojisteni.db"
evidence = EvidencePojistek(db_name)

root = tk.Tk()
root.title("Evidence pojistek")

menu_frame = tk.Frame(root)
menu_frame.pack(side=tk.BOTTOM, fill=tk.X)

pridat_button = tk.Button(menu_frame, text="Přidat pojištěnce", command=pridat_uzivatele)
pridat_button.pack()

seznam_button = tk.Button(menu_frame, text="Seznam pojistěných", command=zobraz_seznam_pojistenych)
seznam_button.pack()

vyhledavani_button = tk.Button(menu_frame, text="Vyhledávání", command=vyhledavani)
vyhledavani_button.pack()

registrace_frame = tk.Frame(root)

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

ulozit_button = tk.Button(registrace_frame, text="Uložit", command=ulozit_uzivatele)
ulozit_button.pack()

vyhledavani_frame = tk.Frame(root)

vyhledavani_label = tk.Label(vyhledavani_frame, text="Hledaný výraz:")
vyhledavani_label.pack()

vyhledavani_entry = tk.Entry(vyhledavani_frame)
vyhledavani_entry.pack()

hledat_button = tk.Button(vyhledavani_frame, text="Hledat", command=hledat_pojistence)
hledat_button.pack()

vypis_text = tk.Text(root)
vypis_text.pack()

root.mainloop()
