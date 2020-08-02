import Model as m
import MonteCarlo as mc


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


def zahtevaj_potezo():
    poteza = input("Vpiši svojo potezo\n>>> ")
    if poteza == 'pass':
        return m.PASS
    else:
        return eval(poteza)


def doloci_mrtve(go):
    kamen = input(
        "Vpiši polje, na katerem se nahaja mrtev kamen (Če jih ni, pritisni enter).\n>>> "
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
        Zadnja poteza: {(lambda x: '' if x == None else x)(go.zadnja_poteza)}
        Za navodila vpiši 'help'.\n\n
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


def zacni():
    velikost = izberi_velikost()
    igra = m.Go(velikost)
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
    kopija = m.deepcopy(igra)
    # Za primer, če se igralca premislita in igro še nadaljujeta, naredimo kopijo.
    while True:
        mrtve = doloci_mrtve(igra)
        if mrtve == None:
            break
        else:
            for mrtva in mrtve:
                kopija.odstrani_mrtvo_grupo(mrtva)
        print(izpis_delnega_rezultata(kopija))
        
        
zacni()
