import Model
import bottle


SKRIVNOST = "velika_skrivnost"
igre = Model.Igre()


@bottle.get("/")
def index():
    return bottle.template("views/index.tpl")


@bottle.get("/static/<filename>")
def server_static(filename):
    return bottle.static_file(filename, root="./views")


@bottle.post("/pvp/")
def pvp():
    if bottle.request.get_cookie("nacin_igre", secret=SKRIVNOST) == None:
        bottle.response.set_cookie("nacin_igre", "pvp", SKRIVNOST, path="/")
    bottle.redirect("/velikost/")


@bottle.get("/velikost/")
def velikost():
    return bottle.template("views/velikost.tpl")


@bottle.post("/<n:int>/")
def st(n):
    cookie = n
    id_igre = igre.doloci_id_igre()
    if bottle.request.get_cookie("velikost", secret=SKRIVNOST) == None:
        bottle.response.set_cookie("velikost", cookie, SKRIVNOST, path="/")
    if bottle.request.get_cookie("id_igre", secret=SKRIVNOST) == None:
        bottle.response.set_cookie("id_igre", id_igre, SKRIVNOST, path="/")
    bottle.redirect("/igra/")


@bottle.get("/igra/")
def igra():
    id_igre = bottle.request.get_cookie("id_igre", secret=SKRIVNOST)
    velikost = bottle.request.get_cookie("velikost", secret=SKRIVNOST)
    nacin_igre = bottle.request.get_cookie("nacin_igre", secret=SKRIVNOST)
    igra = igre.nova_igra(velikost)
    igre.igre[id_igre] = igra
    return bottle.template(
        "views/igra.tpl",
        igra=igra,
        velikost=velikost
        )


bottle.run(reloader=True, debug=True)