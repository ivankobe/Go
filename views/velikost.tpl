% rebase("base.tpl")

<div class="flexbox_vert">

    <div class="pozdrav">
    </div>

    <div class="izbira">
        <h1>Izberi velikost igralne deske:</h1>
    </div>

    <div id="flexbox_velikost">

        <form action=/9/ method="post">
            <button type="submit" class="button_velikost">9</button>
        </form>

        <form action=/13/ method="post">
            <button type="submit" class="button_velikost">13</button>
        </form>

        <form action=/19/ method="post">
            <button type="submit" class="button_velikost">19</button>
        </form>

    </div>

</div>