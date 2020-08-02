from random import randrange, getrandbits, shuffle, choice
from copy import deepcopy

CRNI = 'X'
BELI = 'O'
PASS = 'P'
PREDAJ = 'PR'
NAPREJ = 'N'


class Grupa:

    def __init__(self, barva, koordinata, go):
        i, j = koordinata
        self.barva = barva
        self.koordinate = {koordinata} # Ko je grupa ustvarjena, je najprej vedno dolžine 1
        self.igra = go
        self.sosedje = go.sosedje(koordinata)
        self.svobode = {sosed for sosed in self.sosedje if go.poglej(sosed) == None}
        go.prazna_polja.remove(koordinata)
        go.grupe.append(self)
        go.goban[i][j] = self.barva
        for grupa in go.grupe:
            if grupa.barva != self.barva and koordinata in grupa.svobode:
                grupa.svobode.remove(koordinata)
    
    # Naslednji funkciji implementirata osnovne interakcije med grupami 

    def razsiri_se(self, koordinata):
        i, j = koordinata 
        self.koordinate.add(koordinata)
        self.igra.goban[i][j] = self.barva
        self.sosedje.remove(koordinata)
        self.svobode.remove(koordinata)
        self.igra.prazna_polja.remove(koordinata)
        for sosed in self.igra.sosedje(koordinata):
            if sosed not in self.koordinate:
                self.sosedje.add(sosed)
                if self.igra.poglej(sosed) == None:
                    self.svobode.add(sosed)
        for grupa in self.igra.grupe:
            if self.barva != grupa.barva and koordinata in grupa.svobode:
                grupa.svobode.remove(koordinata)

    def zdruzi_se(self, others, koordinata):
        """Združita se lahko več kot dve grupi naenkrat,
        zato bo drugi argument seznam množic."""
        i, j = koordinata
        self.igra.goban[i][j] = self.barva
        self.igra.prazna_polja.remove(koordinata)
        self.koordinate.add(koordinata)
        for other in others:
            for kamen in other.koordinate:
                self.koordinate.add(kamen)
            for sosed in other.sosedje:
                self.sosedje.add(sosed)
            for svoboda in other.svobode:
                self.svobode.add(svoboda)
            self.sosedje.discard(koordinata)
            self.svobode.discard(koordinata)
            self.igra.grupe.remove(other)
        for grupa in self.igra.grupe:
            if self.barva != grupa.barva and koordinata in grupa.svobode:
                grupa.svobode.remove(koordinata)
        for sosed in self.igra.sosedje(koordinata):
            if sosed not in self.koordinate:
                self.sosedje.add(sosed)
                if self.igra.poglej(sosed) == None:
                    self.svobode.add(sosed)

    def pojej(self):
        indeks = 0 if self.igra.na_potezi() == CRNI else 1
        for kamen in self.koordinate:
            i, j = kamen
            self.igra.goban[i][j] = None
            self.igra.ujetniki[indeks] += 1
            self.igra.prazna_polja.add(kamen)
        self.igra.grupe.remove(self)
        for skupina in self.igra.grupe:              # Preverimo še, ali se je s tem sprostila
            for kamen in self.koordinate:            # svoboda kakšni drugi grupi.
                if kamen in skupina.sosedje:
                    skupina.svobode.add(kamen)


class Go:
    
    def __init__(self, velikost=19, komi=7.5):
        assert velikost in {9, 13, 19}, f'Goban velikosti {velikost} ne obstaja!'
        self.velikost = velikost
        self.komi = komi
        self.goban = [[None] * velikost for i in range(velikost)] # Igralno desko (goban) predstavimo s kvadratno matriko.
        self.koordinate = {(i, j) for i in range(velikost) for j in range(velikost)}
        self.prazna_polja = {(i, j) for i in range(velikost) for j in range(velikost)}
        self.ujetniki = [0, 0] # pr1 je števec za bele ujetnike, pr2 pa za črne
        self.grupe = []
        self.poteza = 0
        self.zadnja_poteza = None
        # Stanja na gobanu hashamo po Zorbistovi metodi. Hash tabela je velikost 2 * 361.
        self.hash_tabela = [[getrandbits(64), getrandbits(64)] for i in range(velikost) for j in range(velikost)]
        # Dodatno 64-bitno število nam bo povedalo, kdo je na potezi
        self.hash_tabela.append(getrandbits(64))
        self.hash = 0
        self.pretekla_stanja = [] # Seznam hash vrednosti preteklih stanj
        self.predaja_poteze = False
        self.konec = False

    def __str__(self):
        niz = ''
        for i in self.goban:
            for j in i:
                if j == CRNI:
                    niz += CRNI
                elif j == BELI:
                    niz += BELI
                else:
                    niz += '.'
                niz += ' '
            niz += '\n'
        return niz
                
    def poglej(self, koordinata):
        """Sprejme koordinato in preveri, kamen katere barve je na njej."""
        i, j = koordinata
        return self.goban[i][j]

    def sosedje(self, koordinata):
        i, j = koordinata
        return {(i + 1, j), (i, j + 1), (i - 1, j), (i, j - 1)} & self.koordinate

    def diagonalni_sosedje(self, koordinata):
        i, j = koordinata
        return {(i + 1, j + 1), (i + 1, j - 1), (i - 1, j + 1), (i - 1, j - 1)} & self.koordinate

    def na_potezi(self):
        if self.poteza % 2 == 0:
            return CRNI
        else:
            return BELI

    def nasprotnik(self):
        if self.poteza % 2 == 0:
            return BELI
        else:
            return CRNI

    def ustvari_novo_grupo(self, koordinata):
        Grupa(self.na_potezi(), koordinata, self)
        
    def najdi_grupo(self, koordinata):
        """Če obstaja, vrne grupo, ki se najaha na dani koordinati."""
        for grupa in self.grupe:
            if koordinata in grupa.koordinate:
                return grupa

    def pojedene_grupe(self, poteza):
        """Vrnemo grupe, ki bi jih dana poteza pojedla."""
        return [
            grupa for grupa in self.grupe if
            grupa.barva == self.nasprotnik() and
            grupa.svobode == {poteza}
            ]

    def poteza_je_samomor(self, koordinata):
        """Poteze, katerih posledica bi bila, da bi dana grupa
        igralca na potezi ostale brez svobod, so prepovedane."""
        if None in {self.poglej(sosed) for sosed in self.sosedje(koordinata)}:
            return False
        za_pojesti = self.pojedene_grupe(koordinata)
        if len(za_pojesti) > 0:
            return False
        sosednje_grupe = [
            grupa for grupa in self.grupe if
            grupa.barva == self.na_potezi() and
            koordinata in grupa.svobode
            ]
        # Seznam grup, katerih del bi postal odigran kamen
        svobode = set()
        for grupa in sosednje_grupe:
            for svoboda in grupa.svobode:
                svobode.add(svoboda)
        return len(svobode) <= 1 
        # Če sosednjih grup ni, je poteza samomor natanko tedaj, ko je len(svobode) == 0,
        # sicer pa natanko tedaj, ko je len(svobode) == 1. 

    def izracunaj_hash(self, poteza):
        """Birokracija okoli hashanja. Apliciramo hash za postavljeni kamen,
        za to, kdo je na potezi, in tudi za morebitne pojedene grupe."""
        i, j = poteza
        zorb = self.hash
        indeks = 0 if self.na_potezi() == CRNI else 1
        zorb ^= self.hash_tabela[i * self.velikost + j][indeks]
        for grupa in self.pojedene_grupe(poteza):
            for kamen in grupa.koordinate:
                k, l = kamen
                zorb ^= self.hash_tabela[k * self.velikost + l][indeks ^ 1] # Vrednost indeks je 0 ali 1, XOR pa jo ravno obrne.
        zorb ^= self.hash_tabela[-1]
        return zorb

    def poteza_krsi_ko(self, poteza):
        """Ko je pravilo, ki prepoveduje poteze, ki bi rezultirale v
        kateri izmed pozicij, ki so tekom dane igre že bile odigrane."""
        return self.izracunaj_hash(poteza) in self.pretekla_stanja

    def poteza_je_dovoljena(self, poteza):
        return all([
            self.poglej(poteza) == None,
            not self.poteza_je_samomor(poteza),
            not self.poteza_krsi_ko(poteza)
            ])

    def dovoljene_poteze(self):
        return {koordinata for koordinata in self.koordinate if self.poteza_je_dovoljena(koordinata)}

    def igraj(self, poteza):
        if poteza == PASS:
            self.poteza += 1
            self.zadnja_poteza = poteza
            if self.predaja_poteze == True:
                self.konec = True
            else:
                self.predaja_poteze = True
        elif poteza == PREDAJA:
            self.konec = True
        else:
            assert all([
                type(poteza) == tuple,
                len(poteza) == 2,
                type(poteza[0]) == int,
                type(poteza[1]) == int,
            ]), "Poteza je nevejlavne oblike. Biti mora številski dvojec."
            assert poteza in self.koordinate, f"Polje {poteza} je izven gobana!"
            assert self.poglej(poteza) == None, f"Polje {poteza} ni prazno!"
            assert not self.poteza_je_samomor(poteza), 'Poteza je samomor!'
            zorb = self.izracunaj_hash(poteza)
            assert zorb not in self.pretekla_stanja, 'Poteza krši pravilo ko!'
            self.predaja_poteze = False
            self.pretekla_stanja.append(self.hash)
            self.hash = zorb
            sosednje_grupe = [
                grupa for grupa in self.grupe if
                grupa.barva == self.na_potezi() and
                poteza in grupa.svobode
                ]
            for grupa in self.pojedene_grupe(poteza):
                grupa.pojej()
            if len(sosednje_grupe) == 0:
                self.ustvari_novo_grupo(poteza)
            elif len(sosednje_grupe) == 1:
                sosednje_grupe[0].razsiri_se(poteza)
            else:
                sosednje_grupe[0].zdruzi_se(sosednje_grupe[1:], poteza)
            self.poteza += 1
            self.zadnja_poteza = poteza


    def tocka_je_robna(self, tocka):
        return set(tocka) & {0, self.velikost - 1} != set()

    def tocka_je_oko(self, tocka):
        """Ker bomo kasneje simulirali igre, se moramo prepričati, da se bodo te igre končale.
        To dosežemo tako, da prepovemo poteze, s katerimi bi igralec zapolnjeval lastna očesa.
        Uporabljena definicija očesa ni povsem natančna, a je za naše potrebe dovolj dobra."""
        if not self.tocka_je_robna(tocka):
            return all([
                self.poglej(tocka) == None,
                [self.poglej(sosed) for sosed in self.sosedje(tocka)].count(self.na_potezi()) == 4,
                [self.poglej(sosed) for sosed in self.diagonalni_sosedje(tocka)].count(self.na_potezi()) >= 3
                ])
        else:
            return all([
                self.poglej(tocka) == None,
                {self.poglej(sosed) for sosed in self.sosedje(tocka) | self.diagonalni_sosedje(tocka)} == {self.na_potezi()}
                ])
    
    # V nadaljevanju definiramo metode za evalvacijo končnih pozicij. Ob
    # tem predpostavljamo, da v končni poziciji na gobanu ni mrtvih kamnov.

    def isci_med_sosedi(self, presecisce, ze_najdeni={}):
        return {
            sosed for sosed in self.sosedje(presecisce) if
            self.poglej(sosed) == None and
            sosed not in ze_najdeni
            }
    
    def isci_med_sosedi_grupa(self, grupa, ze_najdeni={}):
        najdeni = set()
        for presecisce in grupa:
            najdeni |= self.isci_med_sosedi(presecisce, ze_najdeni)
        return najdeni

    def poisci_teritorij(self, koordinata):
        """Poišče slkenjene skupine praznih polj. Vrne par x, tako da je
        pr1(x) množica polj teritorija, pr2(x) pa bodisi barva igralca,
        ki obkroža najdeni teritorij, bodisi None."""
        teritorij = {koordinata}
        novi = {koordinata}
        zid = {self.poglej(sosed) for sosed in self.sosedje(koordinata)}
        while True:
            najdeni = self.isci_med_sosedi_grupa(novi, teritorij)
            teritorij |= najdeni
            for polje in najdeni:
                for sosed in self.sosedje(polje):
                    zid.add(self.poglej(sosed))
            if len(najdeni) == 0:
                break
            novi = najdeni
        zid.discard(None)
        if len(zid) == 1:
            return teritorij, next(iter(zid))
        else:
            return teritorij, None

    def odstrani_mrtvo_grupo(self, grupa):
        """Pomožna funkcija za zaključek igre in evaluacijo teritorija. Tako
        igralcema med igro ne bo treba nujno pojesti vseh mrtvih kamnov."""
        indeks = 0 if grupa.barva == BELI else 1
        for kamen in grupa.koordinate:
            i, j = kamen
            # Add empty point hash code.
            self.goban[i][j] = None
            self.prazna_polja.add(kamen)
            self.ujetniki[indeks] += 1
            # S posodabljanjem ostalih atributov se nam ni treba ukvarjati.
        return None

    def najdi_vse_mrtve(self, grupa):
        """Ko je ena grupa označena za mrtvo, so mrtve tudi vse ostale
        grupe, ki se nahajajo znotraj istega teritorija. Vrnemo seznam
        vseh takih grup. Vrne seznam, ki vsebuje originalno mrtvo grupo
        in tudi vse najdene."""
        barva = grupa.barva
        mrtve = [grupa]
        for svoboda in grupa.svobode:
            teritorij = self.poisci_teritorij(svoboda)[0]
            for polje in teritorij:
                for sosed in self.sosedje(polje):
                    if self.poglej(sosed) == barva:
                        gr = self.najdi_grupo(sosed)
                        if gr not in mrtve:
                            mrtve.append(gr)
        return mrtve

    def prestej_teritorij(self):
        """Vrne par x, tako da je pr1(x) število presečišč v teritorjiju
        črnega, pr2(x) pa v teritoriju belega. Množica mrtve_grupe je unija
        poljubnih podmnožic množic koordinat mrtvih grup."""
        assert self.konec, 'Igre še ni konec, zato ne moremo prešteti teritorija!'
        prazna_polja = {polje for polje in self.koordinate if self.poglej(polje) == None}
        crni, beli = 0, 0
        while len(prazna_polja) > 0:
            polje = next(iter(prazna_polja))
            teritorij, barva = self.poisci_teritorij(polje)
            prazna_polja -= teritorij
            if barva == CRNI:
                crni += len(teritorij)
            elif barva == BELI:
                beli += len(teritorij)
        return crni, beli

    def zmagovalec(self):
        """Vrne število točk v prid črnemu."""
        crni, beli = self.prestej_teritorij()
        beli_u, crni_u = self.ujetniki
        for grupa in self.grupe:
            if grupa.barva == BELI:
                beli += len(grupa.koordinate)
            else:
                crni += len(grupa.koordinate)
        return crni - crni_u + beli_u - beli - self.komi
