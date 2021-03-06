import model
import montecarlo
import threading
import time
import queue
import random


def izberi_velikost():
    velikost = input("Izberi velikost igralne deske (9/13/19)\n>>> ")
    try:
        velikost = int(velikost)
    except:
        print("Prosim, vprši številsko vrednost.\n")
        return izberi_velikost()
    if velikost in {9, 13, 19}:
        return velikost
    else:
        print("Prosim, izberi eno izmed števil 9, 13, 19.\n")
        return izberi_velikost()


def izberi_barvo():
    niz = """Želiš igrati kot črni, kot beli, ali naj 
        bo barva izbrana naključno? (č/b/n)\n>>> """.replace("        ", "")
    barva = input(niz)
    if barva == "č":
        return model.CRNI
    elif barva == "b":
        return model.BELI
    elif barva == "n":
        return random.choice([model.CRNI, model.BELI])
    else:
        print("Prosim, vpiši veljavno vrednost!\n")
        return izberi_barvo()


def izberi_nacin_igre():
    niz = input(
        "Želiš igrati s prijateljem ali proti računalniku? (0/1)\n>>> "
    )
    if niz not in {'0', '1'}:
        print("Prosim, vpiši veljavno vrednost!\n")
        return izberi_nacin_igre()
    else:
        return niz


def zahtevaj_potezo():
    poteza = input("Vpiši svojo potezo\n>>> ")
    if poteza == 'pass':
        return model.PASS
    else:
        return eval(poteza)


def doloci_mrtve(go):
    kamen = input(
        """Vpiši polje, na katerem se nahaja mrtev kamen \
        (Če jih ni, pritisni enter).\n>>> """.replace("        ", "")
        )
    if kamen == "":
        return None
    else:
        try:
            kamen = eval(kamen)
        except:
            raise ValueError("Vnesi veljavno vrednost (dvojico koordinat)!")
        assert kamen in go.koordinate, f"Polja {kamen} ni na gobanu!"
        assert go.poglej(kamen) != None, f"Polje {kamen} je prazno!"
        grupa = go.najdi_grupo(kamen)
        mrtve = go.najdi_vse_mrtve(grupa)
        return mrtve


def izpis_igre(go):
    niz = (
        f"""Na potezi: {go.na_potezi()}
        Beli ujetniki: {go.ujetniki[0]}
        Črni ujetniki: {go.ujetniki[1]}
        Zadnja poteza: {(lambda x: '' if x == None else x)(go.zadnja_poteza)}\n\n
        {go.__str__()}"""
    ).replace("        ","")
    return niz


def izpis_delnega_rezultata(go):
    barva = lambda x: 'črni' if x > 0 else 'beli'
    rezultat = go.zmagovalec()
    niz = (
        f"""Rezultat: {barva(rezultat)} vodi za {abs(rezultat)} točk.\n\n
        {go.__str__()}"""
        ).replace("        ", "")
    return niz


def izpis_koncnega_rezultata(go):
    barva = lambda x: 'črni' if x > 0 else 'beli'
    rezultat = go.zmagovalec()
    niz = (
        f"""Igre je konec!
        {barva(rezultat)} je zmagal za {abs(rezultat)} točk."""
        ).replace("        ", "")
    return niz


def pvp():
    """Vmesnik za igro s prijateljem."""
    velikost = izberi_velikost()
    igra = model.Go(velikost)
    while not igra.konec:
        print(izpis_igre(igra))
        while True:
            poteza = zahtevaj_potezo()
            try:
                igra.igraj(poteza)
                break
            except AssertionError as e:
                print(e)
                print('')
    while True:
        mrtve = doloci_mrtve(igra)
        if mrtve == None:
            break
        else:
            for mrtva in mrtve:
                igra.odstrani_mrtvo_grupo(mrtva)
        print(izpis_delnega_rezultata(igra))
    print(izpis_koncnega_rezultata(igra))


# Zdaj s pomočnjo modula threading definiramo pomožne funkcije,
# ki nam bodo kasneje, pri definiciji vmesnika za igro proti
# računalniku, omogočile, da bo računalnik izvajal simulacije
# tudi medtem ko igralec razmišlja o svoji potezi.


def tuhtaj(mc):
    t = threading.current_thread()
    stanje = mc.stanje
    while getattr(t, "run", True):
    # Zunanja while-zanka se izvaja, dokler igralec ne vnese poteze
        while True:
        # Notranja while-zanka se izvaja, dokler se ena simulacija ne konča 
            neraziskani = mc.neraziskani(stanje)
            if len(neraziskani) > 0:
                izbira = random.choice(list(neraziskani))
                stanje = montecarlo.Vozel(mc, izbira, stanje)
                stanje.simuliraj_igro()
                stanje = mc.stanje
                break
            else:
                stanje = mc.ucb1(stanje)


def tuhtaj_dokler_igralec_ne_vnese_poteze(mc):
    # Objekt razreda Queue potrebujemo, da vanj shranimo
    # vrednost klica funkcije 'zahtevaj_potezo'.
    que = queue.Queue()
    t = threading.Thread(target=tuhtaj, args=(mc,))
    g = threading.Thread(target=lambda q: q.put(zahtevaj_potezo()), args=(que,))
    t.start()
    g.start()
    g.join()        # Najprej počakamo, da se zaključi g.
    t.run = False        # Ustavimo še while-zanko znotraj klica tuhtaj().
    t.join
    return que.get()


def pvb():
    """Vmesnik za igro proti računalniku."""
    velikost = izberi_velikost()
    barva = izberi_barvo()
    igra = model.Go(velikost)
    mc = montecarlo.MonteCarlo(igra)
    while not igra.konec:
        print(izpis_igre(igra))
        if igra.na_potezi() == barva:
            while True:
                poteza = tuhtaj_dokler_igralec_ne_vnese_poteze(mc)
                try:
                    igra.igraj(poteza)
                    mc.stanje = mc.potomec_poteza(poteza)
                    break
                except AssertionError as e:
                    print(e)
                    print('')
        else:
            poteza = mc.najboljsa_poteza()
            igra.igraj(poteza)
    print(izpis_koncnega_rezultata(igra))
        

def main():
    nacin = izberi_nacin_igre()
    if nacin == '0':
        return pvp()
    else:
        return pvb()



if __name__ == "__main__":
    main()
