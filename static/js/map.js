var myMap;

ymaps.ready(init);

function init () {
    myMap = new ymaps.Map('map', {
        center: [55.750754, 37.620532], 
        zoom: 10
    }, {
        restrictMapArea: [
            [55.35,37.12],
            [56.05,38.03]
        ]
    });

    myMap.events.add("balloonopen", function(){
        if (myMap.balloon.isOpen()) {
            myMap.setZoom(16);
        }
    })
    
}



let zoomMap = 11;
let centerMap = { lat: 55.750754, lng: 37.620532};
const MOSCOW_BOUNDS = {
	north: 56.04,
	south: 55.55,
	west: 37.12,
	east: 38.03,
};

$(document).ready(function () {
    var frm = $('#crit-map');
    $('#crit-map').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.ans){
                    $(".notice-box").html("");
                    $("#map-info").html(response.info);
                    if (response.lat){
                        myMap.setCenter([response.lat, response.lng], 14);
                    }
                    addMarker(response.ans);

                }else{
                    $(".notice-box").html(response.error);
                }
            },
            error: function (response) {
                alert(response.responseJSON.errors);
                console.log(response.responseJSON.errors);
            }
        });
        return false;
    });
})


function addMarker (playgrounds) {
    myMap.geoObjects.removeAll();
    for(let i = 0; i < playgrounds.length; i++) {  
        if (playgrounds[i][6]){ 
            ret_str = `<img src="` + playgrounds[i][6] + `" alt="Поле ` + playgrounds[i][0] + `" style="width: 350px; height: 200px;">`;
        }else{
            ret_str = `<img src="/static/img/logo.png" alt="Поле ` + playgrounds[i][0] + `" style="width: 350px; height: 200px;">`;
        }
        if (playgrounds[i][4]){
            ret_str += `<p><a href="` + playgrounds[i][4] + `" class="alert-link" style="color: black; cursor: pointer;">Открыть в картах</a>`;
        }
        if (playgrounds[i][3]){
            ret_str += `<p><i>Это платная площадка</i></p>`;
            mark_color = '#000'
        }else{
            ret_str += `<p><i>Это бесплатная площадка</i></p>`;
            mark_color = '#f00'
        }
        ret_str += `<p>` + playgrounds[i][2] + 
        `<p><i>` + playgrounds[i][5] + `</i>` +            
        `<p><a href="/f/show/` + playgrounds[i][1] + `" style="color: black; cursor: pointer;">Ссылка на площадку</a><br>
        `;
        var placemark = new ymaps.Placemark([playgrounds[i][7], playgrounds[i][8]], {
            balloonContentHeader: playgrounds[i][0],
            balloonContentBody: ret_str}
        , {
            preset: "islands#circleDotIcon",
            hideIconOnBalloonOpen: false,
            iconColor: mark_color
        });
        myMap.geoObjects.add(placemark);
    }
}