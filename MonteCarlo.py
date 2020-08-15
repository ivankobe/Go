import model
import random
import math
import time
import copy


class Vozel:

    # Objekti razreda Vozel so gradniki iskalnega drevesa (nodes).
    
    def __init__(self, mc, poteza=None, parent=None):
        self.poteza = poteza        # Zadnja odigrana poteza
        self.mc = mc        # Referenca na iskalno drevo (objekt razreda MonteCarlo)
        self.parent = parent
        self.mc.vozli[self] = set(), set()
        self.stevilo_simulacij = 0
        self.stevilo_zmag = 0
        if parent == None:
            # Barva vozla je barva zadnjega odigranega kamna
            self.barva = None
            self.igra = model.Go(self.mc.velikost)
        else:
            if parent.barva == model.CRNI:
                self.barva = model.BELI
            else:
                self.barva = model.CRNI
            self.mc.vozli[self.parent][0].add(self)
            self.igra = copy.deepcopy(self.parent.igra)
            self.igra.igraj(poteza)
        for poteza in self.igra.dovoljene_poteze():
            self.mc.vozli[self][1].add(poteza)
        # mc.vozli je torej slovar, katerega ključi so vozli, njigove
        # vrednosti pa so dvojice x, tako da je pr1(x) množica vseh že
        # raziskanih potomcev (se pravi vozlov), pr2(x) pa množica vseh
        # dovoljenih potez v poziciji, ki jo predstavlja dani vozel.

    def zabelezi_rezultat(self, rezultat):
        """Glede na rezultat simulacije posodobi stanje iskalnega drevesa.
        
        Sebi, kot tudi vsem vozlom, ki so nad njim, poveča število simulacij
        za ena, v primeru, da je zmagovalec simulirane igre igralec na potezi,
        pa sebi in sebi nadrejenim vozlom za ena poveča tudi število zmag.
        """
        zmagovalec = model.CRNI if rezultat > 0 else model.BELI
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
            """Odigramo naključno igro. Vrnemo rezultat."""
            igra = copy.deepcopy(self.igra)
            while not igra.konec:
                na_voljo = list(igra.prazna_polja)
                while True:
                    if len(na_voljo) > 0:
                        poteza = random.choice(na_voljo)
                        if not igra.tocka_je_oko(poteza):
                            try:
                                igra.igraj(poteza)
                                break
                            except AssertionError:
                                na_voljo.remove(poteza)
                        else:
                            na_voljo.remove(poteza)
                    else:
                        igra.igraj(model.PASS)
                        break
            rezultat = igra.zmagovalec()
            self.zabelezi_rezultat(rezultat)
            return rezultat


class MonteCarlo:

    # Iskalno drevo

    def __init__(self, igra):

        self.igra = igra
        self.velikost = self.igra.velikost
        self.vozli = {}
        self.stanje = Vozel(self)
        # Atribut cas je stevilo sekund, ki si jih
        # računalnik vzame za premislek za izbiro poteze.
        self.cas = 3

    def potomec_poteza(self, poteza):
        """Poišče/ustvari vozel, ki ustreza dani potezi."""
        # Najprej preverimo, ali iskani vozel že obstaja:
        for vozel in self.vozli[self.stanje][0]:
            if vozel.poteza == poteza:
                return vozel
        # V nasprotnem primeru preverimo, ali je poteza dovoljena:
        if poteza in self.vozli[self.stanje][1]:
            potomec = Vozel(self, poteza, self.stanje)
            return potomec
        else:
            return

    def ucb1(self, vozel):
        """Upper confidence bound 1."""
        ucb = lambda vozel: (
            vozel.stevilo_zmag / vozel.stevilo_simulacij +
            math.sqrt(
                2 * (math.log(vozel.parent.stevilo_simulacij) / vozel.stevilo_simulacij)
                )
            )
        return max(self.vozli[vozel][0], key=ucb)
            
    def neraziskani(self, vozel):
        """Vrne množico dovoljenih potez, ki jih še nismo raziskali."""
        return (
            self.vozli[vozel][1] -
            {potomec.poteza for potomec in self.vozli[vozel][0]}
        )

    def najboljsa_poteza(self):
        """Za  pozicijo aproksimira najboljšo potezo in jo vrne.
        
        Pozor: funkcija avtomatično spremeni stanje iskalnega drevesa. 
        """
        stanje = self.stanje
        zacetek = time.time()
        if len(self.vozli[stanje][1]) == 0:
            # Če ni dovoljenih potez, se odrečemo potezi.
            return model.PASS
        elif (
            self.igra.zadnja_poteza == model.PASS
            and self.igra.zmagovalec_na_potezi()
            ):
            # Če se nasprotnik odreče potezi in smo v prednosti, se ji odrečemo tudi mi.
            return model.PASS
        else:
            while time.time() - zacetek < self.cas:
                neraziskani = self.neraziskani(stanje)
                if len(neraziskani) > 0:
                    izbira = random.choice(list(neraziskani))
                    stanje = Vozel(self, izbira, stanje)
                    stanje.simuliraj_igro()
                    stanje = self.stanje
                else:
                    stanje = self.ucb1(stanje)
            najboljsa = lambda vozel: vozel.stevilo_zmag / vozel.stevilo_simulacij
            najboljsi_potomec = max(self.vozli[self.stanje][0], key=najboljsa)
            # Če je procent zmag najobetavnejšega potomca
            # manjši od ene desetine, igro predamo.
            if najboljsa(najboljsi_potomec) < 0.1:
                return model.PREDAJA
            else:
                # Na koncu posodobimo stanje iskalnega drevesa.
                self.stanje = najboljsi_potomec
                return najboljsi_potomec.poteza
