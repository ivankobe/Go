from random import randrange, getrandbits, shuffle, choice
from copy import deepcopy


CRNI = 'X'
BELI = 'O'
PASS = 'P'
PREDAJA = 'PR'


class Grupa:

    def __init__(self, barva, koordinata, go):
        self.barva = barva
        self.koordinate = {koordinata}
        self.igra = go
        self.sosedje = self.igra.sosedje(koordinata)
        
    def zdruzi_se(self, others, koordinata):
        """Združita se lahko več kot dve grupi naenkrat,
        zato bo drugi argument seznam množic.
        """
        for other in others:
            self.koordinate |= other.koordinate
            self.svobode -= {koordinata}
            self.igra.grupe.remove(other)


class Go:
    
    def __init__(self, velikost=19):
        assert velikost in {9, 13, 19}, f'Goban velikosti {velikost} ne obstaja!'
        self.velikost = velikost
        self.komi = 6.5
        self.goban = [[None] * velikost for i in range(velikost)]
        # Igralno desko (goban) predstavimo s kvadratno matriko.
        self.koordinate = {(i, j) for i in range(velikost) for j in range(velikost)}
        self.prazna_polja = {(i, j) for i in range(velikost) for j in range(velikost)}
        self.ujetniki = [0, 0] # pr1 je števec za bele ujetnike, pr2 pa za črne
        self.grupe = []
        self.poteza = 0
        self.zadnja_poteza = None
        # Stanja na gobanu hashamo po Zorbistovi metodi. Hash tabela je velikost 2 * (velikost ** 2)
        self.hash_tabela = [[getrandbits(64), getrandbits(64)] for i in range(velikost) for j in range(velikost)]
        # Dodatno 64-bitno število nam bo povedalo, kdo je na potezi
        self.hash_tabela.append(getrandbits(64))
        self.hash = 0
        self.pretekla_stanja = [] # Seznam hash vrednosti preteklih stanj
        self.poteze = []
        # Atribut bo prišel prav za omogočanje 'undo'-ja
        self.bot = None
        # Atribut določimo v primeru igre proti računalniku. Glede na to,
        # katere barve je bot, ima vrednost BELI ali CRNI.
        self.predaja_poteze = False
        self.konec = False
        self.konec_konca = False
        # Relevantno zgolj za spletno različico

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
        return {
            koordinata for koordinata in self.koordinate
            if self.poteza_je_dovoljena(koordinata)
            }

    def pojej(self, grupa):
        indeks = 0 if self.na_potezi() == CRNI else 1
        for kamen in grupa.koordinate:
            i, j = kamen
            self.goban[i][j] = None
            self.ujetniki[indeks] += 1
            self.prazna_polja.add(kamen)
        self.grupe.remove(grupa)
        sosednje_grupe = {
            self.najdi_grupo(sosed) for sosed in grupa.sosedje
            if self.poglej(sosed) != None
        }
        for gr in sosednje_grupe:
            gr.svobode |= gr.sosedje & grupa.koordinate

    def postavi_kamen(self, poteza):
        i, j = poteza
        barva = self.na_potezi()
        grupa = Grupa(barva, poteza, self)
        sosednje_grupe = {
            self.najdi_grupo(sosed) for sosed in self.sosedje(poteza)
            if self.poglej(sosed) != None
            }
        igralceve = []
        nasprotnikove = []
        svobode = set()
        for gr in sosednje_grupe:
            if gr.barva == self.na_potezi():
                igralceve.append(gr)
                svobode |= gr.svobode
                grupa.sosedje |= gr.sosedje
            else:
                nasprotnikove.append(gr)
                if gr.svobode == {poteza}:
                    self.pojej(gr)
        grupa.svobode = {
            sosed for sosed in grupa.sosedje
            if self.poglej(sosed) == None
            } | svobode
        if igralceve == []:
            assert len(grupa.svobode) > 0, "Poteza je samomor!"
        else:
            assert len(grupa.svobode) > 1, "Poteza je samomor!"
            grupa.zdruzi_se(igralceve, poteza)
        for gr in nasprotnikove:
            gr.svobode.remove(poteza)
        self.grupe.append(grupa)
        self.goban[i][j] = barva
        self.prazna_polja.remove(poteza)

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
            self.zadnja_poteza = poteza
        else:
            assert all([
                type(poteza) == tuple,
                len(poteza) == 2,
                type(poteza[0]) == int,
                type(poteza[1]) == int,
            ]), "Poteza je nevejlavne oblike. Biti mora številski dvojec."
            assert poteza in self.koordinate, f"Polje {poteza} je izven gobana!"
            assert self.poglej(poteza) == None, f"Polje {poteza} ni prazno!"
            # assert not self.poteza_je_samomor(poteza), 'Poteza je samomor!'
            zorb = self.izracunaj_hash(poteza)
            assert zorb not in self.pretekla_stanja, 'Poteza krši pravilo ko!'
            try:
                self.postavi_kamen(poteza)
            except AssertionError as e:
                raise e
            self.predaja_poteze = False
            self.pretekla_stanja.append(self.hash)
            self.hash = zorb
            self.poteza += 1
            self.poteze.append(poteza)
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
            self.goban[i][j] = None
            self.prazna_polja.add(kamen)
            self.ujetniki[indeks] += 1
            # S posodabljanjem ostalih atributov se nam ni treba ukvarjati.
        return None

    def najdi_vse_mrtve(self, gr):
        """Ko je ena grupa označena za mrtvo, so mrtve tudi vse ostale
        grupe, ki se nahajajo znotraj istega teritorija. Vrnemo seznam
        vseh takih grup. Vrne seznam, ki vsebuje originalno mrtvo grupo
        in tudi vse najdene. Argument mora biti podmnožica množice
        koordinat dane grupe."""
        kamen = next(iter(gr))
        grupa = self.najdi_grupo(kamen)
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

    def zmagovalec_na_potezi(self):
        """Če je zmagovalec igralec na potezi,
        vrne True, sicer vrne False."""
        return (
            (self.na_potezi() == CRNI and self.zmagovalec() > 0)
            or
            (self.na_potezi() == BELI and self.zmagovalec() < 0)
        )

    def undo(self):
        """Igro vrnemo v prejšnje stanje"""
        kopija = Go(self.velikost)
        for poteza in self.poteze[:-1]:
            kopija.igraj(poteza)
        kopija.bot = self.bot
        return kopija    


class Igre:

    def __init__(self):
        self.igre = {}

    def doloci_id_igre(self):
        if len(self.igre) == 0:
            return 0
        else:
            return max(self.igre.keys()) + 1
    
    def nova_igra(self, velikost):
        igra = Go(velikost)
        id_igre = self.doloci_id_igre()
        self.igre[id_igre] = igra
        return id_igre, igra

    def igraj(self, id_igre, poteza):
        self.igre[id_igre].igraj(poteza)
        