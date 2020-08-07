% rebase("base.tpl")

<div class="flexbox_hor">

    <div id="goban">
        
% for i in range(velikost + 1):
        <div class="vrstica">

% for j in range(velikost + 1):
            <div class="polje"></div>
% end
        </div>
% end

    </div>
</div>