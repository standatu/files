class Pojisteny:
    # Konstruktor pro třídu Pojisteny
    def __init__(self, jmeno, prijmeni, vek, telefon):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.vek = vek
        self.telefon = telefon

    # Metoda pro výpis informací o pojištěném
    def __str__(self):
        return f'Pojisteny({self.jmeno}, {self.prijmeni}, {self.vek}, {self.telefon})'


class EvidencePojistek:
    # Konstruktor pro třídu EvidencePojistek
    def __init__(self):
        self.pojisteni = []

    # Metoda pro přidání pojištěného do evidence
    def pridat_pojisteneho(self, jmeno, prijmeni, vek, telefon):
        clovek = Pojisteny(jmeno, prijmeni, vek, telefon)
        self.pojisteni.append(clovek)

    # Metoda pro výpis všech pojištěných v evidenci
    def seznam_pojistenych(self):
        for clovek in self.pojisteni:
            print(clovek)

    # Metoda pro vyhledání pojištěného podle jména a příjmení
    def najit_pojisteneho(self, jmeno, prijmeni):
        for clovek in self.pojisteni:
            if clovek.jmeno == jmeno and clovek.prijmeni == prijmeni:
                return clovek
        return None

# Hlavní funkce programu
def main():
    evidence = EvidencePojistek()

    while True:
        print("\n1. Pridat pojisteneho")
        print("2. Seznam vsech pojistenych")
        print("3. Najit pojisteneho")
        print("4. Konec")

        volba = input("Zadejte svoji volbu: ")

        # Přidání pojištěného
        if volba == '1':
            jmeno = input("Zadejte jmeno: ")
            prijmeni = input("Zadejte prijmeni: ")
            vek = int(input("Zadejte vek: "))
            telefon = input("Zadejte telefonni cislo: ")
            evidence.pridat_pojisteneho(jmeno, prijmeni, vek, telefon)

        # Výpis všech pojištěných
        elif volba == '2':
            evidence.seznam_pojistenych()

        # Vyhledání pojištěného
        elif volba == '3':
            jmeno = input("Zadejte jmeno: ")
            prijmeni = input("Zadejte prijmeni: ")
            clovek = evidence.najit_pojisteneho(jmeno, prijmeni)
            if clovek is not None:
                print(clovek)
            else:
                print("Pojisteny nebyl nalezen")

        # Konec programu
        elif volba == '4':
            break


if __name__ == '__main__':
    main()
