%rebase("base.tpl")

<div class="flexbox_vert">

    <div class="pozdrav">
        <h1>Pozdravljen na serverju za  miselno igro go!</h1>
    </div>

    <div class="izbira">
        <h2>Prosim, izberi eno izmed možnosti:</h2>
    </div>

    <div id="box_index">
        
        <form action="/pvp/" method="post">
            <button type="submit" class="button_index">Igraj s prijateljem</button>
        </form>

        <form action="/pvb/" method="post">
            <button type="submit" class="button_index">Igraj proti računalniku</button>
        </form>

        <form action="http://playgo.to/iwtg/slovenian/" method="get">
            <button type="submit" class="button_index">Pravila igre</button>
        </form>

    </div>

</div>
