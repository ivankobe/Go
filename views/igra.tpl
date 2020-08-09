% rebase("base.tpl")
% import Model 

<div class="flexbox_hor">

    <div id="goban">
        
% for i in range(velikost):
        <div class="vrstica">

% # določanje css razreda za izris gobana
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

% # določanje css razreda za pozicijo in nedovoljene poteze

% polje = igra.poglej((i, j))
% if polje == Model.CRNI:
%     razred += "crni "
% elif polje == Model.BELI:
%     razred += "beli "
% else:
%     razred += "prazno "
%     if igra.poteza_je_samomor((i, j)):
%         razred += "samomor "
%     elif igra.poteza_krsi_ko((i, j)):
%         razred += "ko "
% end
% end


% if igra.na_potezi() == Model.BELI:
%     razred += "na_potezi_beli"
% else:
%     razred += "na_potezi_crni"
% end



% if igra.konec:
%     razred += "konec "
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
            
            <h1>konec</h1>
            
% end

       
    </div>


</div>
