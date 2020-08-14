import Model
import MonteCarlo
import bottle
import threading
from random import choice


SKRIVNOST = "velika_skrivnost"
igre = Model.Igre()
simulacije = {}
# Slovar z objekti razreda 'MonteCarlo'.
# Ključi so enaki ključem slovarja 'igre'.


@bottle.get("/")
def index():
    return bottle.template("views/index.tpl")


@bottle.get("/static/<filename>")
def server_static(filename):
    return bottle.static_file(filename, root="./views")


@bottle.post("/pvp/")
def pvp():
    if bottle.request.get_cookie("nacin_igre") == None:
        bottle.response.set_cookie("nacin_igre", "pvp", path="/")
    bottle.redirect("/velikost/")


@bottle.post("/pvb/")
def pvb():
    if bottle.request.get_cookie("nacin_igre") == None:
        bottle.response.set_cookie("nacin_igre", "pvb", path="/")
    bottle.redirect("/velikost/")


@bottle.get("/velikost/")
def velikost():
    return bottle.template("views/velikost.tpl")


@bottle.post("/<n:int>/")
def st(n):
    id_igre, igra = igre.nova_igra(n)
    if bottle.request.get_cookie("nacin_igre") == "pvb":
        igra.bot = choice([Model.BELI, Model.CRNI])
        # Barvo izberemo naključno
        mc = MonteCarlo.MonteCarlo(igra)
        simulacije[id_igre] = mc
    cookie = str(n)
    id_igre = str(id_igre)
    if bottle.request.get_cookie("velikost") == None:
        bottle.response.set_cookie("velikost", cookie, path="/")
    if bottle.request.get_cookie("id_igre") == None:
        bottle.response.set_cookie("id_igre", id_igre, path="/")
    bottle.redirect("/igra/")


@bottle.get("/igra/")
def igra():
    nacin = bottle.request.get_cookie("nacin_igre")
    id_igre = int(bottle.request.get_cookie("id_igre"))
    velikost = int(bottle.request.get_cookie("velikost"))
    igra = igre.igre[id_igre]
    if igra.bot == igra.na_potezi():
        mc = simulacije[id_igre]
        poteza = mc.najboljsa_poteza()
        igra.igraj(poteza)
    return bottle.template(
        "views/igra.tpl",
        id_igre=id_igre,
        igra=igra,
        velikost=velikost,
        nacin=nacin
        )


@bottle.post("/igra/<i:int>_<j:int>/")
def igra_poteza(i ,j):
    poteza = i, j
    id_igre = int(bottle.request.get_cookie("id_igre"))
    nacin = bottle.request.get_cookie("nacin_igre")
    igra = igre.igre[id_igre]
    if not igra.konec:
    # Dokler je igra aktivna, je to ukaz za igranje poteze
        igra.igraj(poteza)
        if nacin == "pvb":
            mc = simulacije[id_igre]
            mc.stanje = mc.potomec_poteza(poteza)
    else:
    # Sicer je klic strani ukaz za odstranjitev mrtvih kamnov
        mrtve = igra.najdi_vse_mrtve({(i, j)})
        for mrtva in mrtve:
            igra.odstrani_mrtvo_grupo(mrtva)
    bottle.redirect("/igra/")


@bottle.post("/igra/pass/")
def passs():
    id_igre = int(bottle.request.get_cookie("id_igre"))
    igra = igre.igre[id_igre]
    igra.igraj(Model.PASS)
    bottle.redirect("/igra/")


@bottle.post("/igra/resign/")
def resign():
    id_igre = int(bottle.request.get_cookie("id_igre"))
    igra = igre.igre[id_igre]
    igra.igraj(Model.PREDAJA)
    bottle.redirect("/igra/")


@bottle.post("/igra/undo/")
def undo():
    id_igre = int(bottle.request.get_cookie("id_igre"))
    nacin = bottle.request.get_cookie("nacin_igre")
    igre.igre[id_igre] = igre.igre[id_igre].undo()
    # Zamenjamo vrednost ključa, saj funkcija
    # 'undo' vrne novo instanco razreda 'Go'
    simulacije[id_igre].stanje = simulacije[id_igre].stanje.parent 
    # Prilagodimo stanje iskalnega drevesa
    if nacin == "pvb":
        igre.igre[id_igre] = igre.igre[id_igre].undo()
        simulacije[id_igre].stanje = simulacije[id_igre].stanje.parent 
        # Če gre za igro proti računalniku,
        # je treba nazaj vzeti dve potezi
    bottle.redirect("/igra/")    


@bottle.post("/igra/konec/")
def konec():
    id_igre = int(bottle.request.get_cookie("id_igre"))
    igra = igre.igre[id_igre]
    igra.konec_konca = True
    bottle.redirect("/igra/")    


@bottle.post("/nova_igra/")
def nova_igra():
    bottle.response.set_cookie("nacin_igre", '', expires=0, path="/")
    bottle.response.set_cookie("velikost", '', expires=0, path="/")
    bottle.response.set_cookie("id_igre", '', expires=0, path="/")
    bottle.redirect("/")


bottle.run(reloader=True, debug=True)
