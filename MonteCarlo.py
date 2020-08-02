import Model as m
from random import choice, shuffle
from math import sqrt, log
from time import time
from copy import deepcopy


class Vozel:

    # Objekti razreda Vozel so gradniki iskalnega drevesa in
    # vsebujejo vse informacije, relevantne za simulacije.

    def __init__(self, mc, poteza=None, parent=None):
        self.velikost = mc.velikost
        self.poteza = poteza # Zadnja odigrana poteza
        self.mc = mc # Referenca na iskalno drevo (objekt razreda MonteCarlo)
        self.parent = parent
        self.potomci = set() # Množica vseh že raziskanih potomcov v drevesu
        self.stevilo_simulacij = 0
        self.stevilo_zmag = 0
        self.igra = m.Go(self.velikost)
        self.barva = self.igra.na_potezi()
        mc.vozli.add(self)
        if self.parent == None:
            self.igra = m.Go(self.velikost)
        else:
            self.igra = deepcopy(parent.igra)
            self.igra.igraj(poteza)
            self.parent.potomci.add(self)
        
    def zabelezi_rezultat(self, rezultat):
        """Sebi, kot tudi vsem vozlom, ki so nad njim, poveča število simulacij
        za ena, v primeru, da je zmagovalec simulirane igre igralec na potezi,
        pa sebi in sebi nadrejenim vozlom za ena poveča tudi število zmag."""
        zmaga = (rezultat > 0 and self.barva == m.CRNI) or (rezultat < 0 and self.barva == m.BELI)
        vozel = self
        while True:
            vozel.stevilo_simulacij += 1
            if zmaga:
                vozel.stevilo_zmag += 1
            if vozel.parent == None:
                break
            else:
                vozel = vozel.parent
        return
            
    def simuliraj_igro(self):
            """Iz pozicije, predstavljene z danim vozlom,
            odigramo naključno igro. Vrnemo rezultat."""
            igra = deepcopy(self.igra)
            while not igra.konec:
                na_voljo = list(self.igra.prazna_polja)
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
                        igra.igraj(m.PASS)
                        break
            rezultat = igra.zmagovalec()
            self.zabelezi_rezultat(rezultat)
            return rezultat


class MonteCarlo:

    def __init__(self, velikost=19, cas=5):
        # Drugi argument je maksimalni čas, ki
        # si ga računalnik lahko vzame za potezo.
        self.vozli = set()
        self.velikost = velikost
        self.izhodisce = Vozel(self)
        # To je edini vozel, do katerega nam bo kdaj treba neposredno dostopati
        self.vozli.add(self.izhodisce)
        self.cas = cas

    def ucb1(self, vozel):
        """V primeru, da za vsako dovoljeno potezo že obstaja
        ustrezen vozel, funkcija ucb1 izbere enega izmed potomcev."""
        ucb = lambda vozel: (
            vozel.stevilo_zmag / vozel.stevilo_simulacij +
            sqrt(2 * (log(vozel.parent.stevilo_simulacij) / vozel.stevilo_simulacij))
            )
        return max(vozel.potomci, key=ucb)
            
    def neraziskani(self, vozel):
        """Vrne množico dovoljenih potez, ki jih še nismo raziskali."""
        return {
            poteza for poteza in vozel.igra.dovoljene_poteze()
            if poteza not in {potomec.poteza for potomec in vozel.potomci}
        }

    def najboljsa_poteza(self, vozel):
        """Za dano pozicijo aproksimira najboljšo potezo in jo vrne."""
        stanje = vozel
        zacetek = time()
        while time() - zacetek < self.cas:
            neraziskani = self.neraziskani(stanje)
            if len(neraziskani) > 0:
                izbira = choice(list(neraziskani))
                stanje = Vozel(self, izbira, stanje)
                stanje.simuliraj_igro()
                stanje = vozel
            else:
                stanje = self.ucb1(stanje)
        najboljsa = lambda vozel: vozel.stevilo_zmag
        return max(vozel.potomci, key=najboljsa)

    def razmisljaj(self, vozel):
        raise NotImplementedError

