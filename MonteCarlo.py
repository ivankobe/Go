import Model
from random import choice, shuffle
from math import sqrt, log
from time import time
from copy import deepcopy


class Vozel:

    # Objekti razreda Vozel so gradniki iskalnega drevesa
    
    def __init__(self, mc, poteza=None, parent=None):
        self.poteza = poteza # Zadnja odigrana poteza
        self.mc = mc # Referenca na iskalno drevo (objekt razreda MonteCarlo)
        self.parent = parent
        self.mc.vozli[self] = set(), set()
        self.stevilo_simulacij = 0
        self.stevilo_zmag = 0
        if parent == None:
            self.igra = Model.Go(self.mc.velikost) # Vsak vozel ima svojo kopijo igre
        else:
            self.mc.vozli[self.parent][0].add(self)
            self.igra = deepcopy(self.parent.igra)
            self.igra.igraj(poteza)
        self.barva = self.igra.na_potezi()
        for poteza in self.igra.dovoljene_poteze():
            self.mc.vozli[self][1].add(poteza)
        # mc.vozli je torej slovar, katerega ključi so vozli, njigove vrednosti pa so dvojice x,
        # tako da je pr1(x) množica vseh že raziskanih potomcev (se pravi vozlov), pr2(x) pa
        # množica vseh dovoljenih potez v poziciji, ki jo predstavlja dani vozel.

    def zabelezi_rezultat(self, rezultat):
        """Sebi, kot tudi vsem vozlom, ki so nad njim, poveča število simulacij
        za ena, v primeru, da je zmagovalec simulirane igre igralec na potezi,
        pa sebi in sebi nadrejenim vozlom za ena poveča tudi število zmag."""
        zmagovalec = Model.CRNI if rezultat > 0 else Model.BELI
        vozel = self
        while True:
            vozel.stevilo_simulacij += 1
            if vozel.barva == zmagovalec:
                vozel.stevilo_zmag += 1
            if vozel.parent == None:
                break
            else:
                vozel = vozel.parent
            
    def simuliraj_igro(self):
            """Iz pozicije, predstavljene z danim vozlom,
            odigramo naključno igro. Vrnemo rezultat."""
            igra = deepcopy(self.igra)
            while not igra.konec:
                na_voljo = list(igra.prazna_polja)
                while True:
                    if len(na_voljo) > 0:
                        poteza = choice(na_voljo)
                        if not igra.tocka_je_oko(poteza):
                            try:
                                igra.igraj(poteza)
                                break
                            except AssertionError:
                                na_voljo.remove(poteza)
                        else:
                            na_voljo.remove(poteza)
                    else:
                        igra.igraj(Model.PASS)
                        break
            rezultat = igra.zmagovalec()
            self.zabelezi_rezultat(rezultat)
            return rezultat


class MonteCarlo:

    # Iskalno drevo

    def __init__(self, igra, cas=5):
        # Drugi argument je maksimalni čas, ki
        # si ga računalnik lahko vzame za potezo.
        self.igra = igra
        self.velikost = self.igra.velikost
        self.vozli = {}
        self.stanje = Vozel(self)
        self.cas = cas

    def ucb1(self, vozel):
        """V primeru, da za vsako dovoljeno potezo že obstaja
        ustrezen vozel, funkcija ucb1 izbere enega izmed potomcev."""
        ucb = lambda vozel: (
            vozel.stevilo_zmag / vozel.stevilo_simulacij +
            sqrt(2 * (log(vozel.parent.stevilo_simulacij) / vozel.stevilo_simulacij))
            )
        return max(self.vozli[vozel][0], key=ucb)
            
    def neraziskani(self, vozel):
        """Vrne množico dovoljenih potez, ki jih še nismo raziskali."""
        return self.vozli[vozel][1] - {potomec.poteza for potomec in self.vozli[vozel][0]}

    def najboljsa_poteza(self):
        """Za  pozicijo aproksimira najboljšo potezo in jo vrne."""
        stanje = self.stanje
        zacetek = time()
        if len(self.vozli[self.stanje][1]) == 0:
            # Če ni dovoljenih potez, se odrečemo potezi
            return Model.PASS
        elif self.igra.zadnja_poteza == Model.PASS and self.igra.zmagovalec_na_potezi():
            # Če se nasprotnik odreče potezi in smo v prednosti, se ji odrečemo tudi mi 
            return Model.PASS
        else:
            while time() - zacetek < self.cas:
                neraziskani = self.neraziskani(stanje)
                if len(neraziskani) > 0:
                    izbira = choice(list(neraziskani))
                    stanje = Vozel(self, izbira, stanje)
                    stanje.simuliraj_igro()
                    stanje = self.stanje
                else:
                    stanje = self.ucb1(stanje)
            najboljsa = lambda vozel: vozel.stevilo_zmag / vozel.stevilo_simulacij
            najboljsi_potomec = max(self.vozli[self.stanje][0], key=najboljsa)
            # Če je procent zmag najobetavnejšega potomca
            # manjši od ene desetine, igro predamo
            if najboljsa(najboljsi_potomec) < 0.1:
                return Model.PREDAJA
            else:
                return najboljsi_potomec


go = Model.Go(9)
mc = MonteCarlo(go)
n = time()
(mc.stanje).simuliraj_igro()
print(time() - n)