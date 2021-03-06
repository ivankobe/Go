% rebase("base.tpl")
% import model 

<div class="flexbox_hor">

    <div id="goban">
        
% for i in range(velikost):
        <div class="vrstica">

%     for j in range(velikost):
%         razred = "polje "
%         if i == 0:
%             razred += "zgoraj "
%         elif i == velikost - 1:
%             razred += "spodaj "
% end
%         if j == 0:
%             razred += "levo "
%         elif j == velikost - 1:
%             razred += "desno "
% end
%         if razred == "polje ":
%             razred += "sredina "
% end


% polje = igra.poglej((i, j))
% if polje == model.CRNI:
%     razred += "crni "
% elif polje == model.BELI:
%     razred += "beli "
% else:
%     razred += "prazno "
%     if igra.poteza_je_samomor((i, j)):
%         razred += "samomor "
%     elif igra.poteza_krsi_ko((i, j)):
%         razred += "ko "
% end
% end


% if not igra.konec:
%     if igra.na_potezi() == model.BELI:
%         razred += "na_potezi_beli "
%     else:
%         razred += "na_potezi_crni "
% end
% end


% if igra.konec:
%     razred += "konec "
% end

% if (i, j) == igra.zadnja_poteza:
%     razred+= "zadnja "
% end


% razred = "'" + razred + "'"

            <form action="/igra/{{i}}_{{j}}/" method="POST">
                <button class={{! razred}}></button>
            </form>

% end
        </div>
% end

    </div>


    <div class="flexbox_vert" id="flexbox_vert_igra">

% if not igra.konec_konca:
% if not igra.konec:
        
        <div class="flexbox_vert" id="flexbox_vert_igra_notranja">

            <h2>Število belih ujetnikov: {{igra.ujetniki[0]}}</h2>
            <h2>Število črnih ujetnikov: {{igra.ujetniki[1]}}</h2>
        
        </div>
        

        <div id="flexbox_hor_igra">
            
            <form action="/igra/pass/" method="POST">
                <button class="button_igra">PASS</button>
            </form>
            
            <form action="/igra/resign/" method="POST">
                <button class="button_igra">PREDAJ</button>
            </form>

            <form action="/igra/undo/" method="POST">
                <button class="button_igra">UNDO</button>
            </form>

        </div>

% else:

        <div class="flexbox_vert" id="flexbox_vert_igra_notranja">
        
            <h2>Označi mrtve kamne!</h2>
        
        </div>


        <div id="flexbox_hor_igra">

            <form action="/igra/konec/" method="POST">
                <button class="button_igra">KONEC</button>
            </form>
        
        </div>
            
% end
% else:
% rezultat = igra.zmagovalec()
% zmagovalec = "črni" if rezultat > 0 else "beli"

    <div class="flexbox_vert" id="flexbox_vert_igra_notranja">

        <h1>Zmagal je {{zmagovalec}} za {{abs(rezultat)}} točk razlike.</h1>

    </div>

    <div id="flexbox_hor_igra">

        <form action="/nova_igra/" method="POST">
            <button class="button_igra">NOVA</button>
        </form>
    
    </div>

% end
       
    </div>


</div>
