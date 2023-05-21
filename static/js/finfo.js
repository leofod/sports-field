$(document).ready(function () {
    var frm = $('#favor');
    $('#favor').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.ans){
                    document.getElementById('favor-b').value = 'Из избранного';
                }else{
                    document.getElementById('favor-b').value = 'В избранное';
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

$(document).ready(function () {
    var frm = $('#add-raiting');
    $('#add-raiting').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.empty_mark){
                    window.location.href = "http://127.0.0.1:8000/";
                } else {
                    document.getElementById('rating-area').setAttribute("style", "display:none");
                    if ((response.ans)){
                        document.getElementById('rating-result').setAttribute("style", "display:all");
                    }
                    let ret_str = `<p>Ваша текущая оценка:</p>\n`;
                    for (let i = 0; i < response.mark; i++){	
                        ret_str += `<span class="active"></span>\n`;
                    }
                    for (let i = 0; i < 5-response.mark; ++i){
                        ret_str += `<span></span>\n`;
                    }
                    $("#rating-result").html(ret_str);
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

$(document).ready(function () {
    var frm = $('.signUp');
    $('.signUp').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.date){
                    if (response.ans){
                        document.getElementById('signUp-b-'+response.date).value = 'Не буду';
                        document.getElementById('signUp-b-'+response.date).setAttribute("style", "background-color: #bc4626;")
                    }else{
                        document.getElementById('signUp-b-'+response.date).value = 'Буду';
                        document.getElementById('signUp-b-'+response.date).setAttribute("style", "background-color: #059e30;")
                    }
                    $("#notif-sign-in").html('');
                    document.getElementById('notif-sign-in').setAttribute("style", "dispslay: none;");
                } else {
                    $("#notif-sign-in").html('Вы не можете записаться.');
                    document.getElementById('notif-sign-in').setAttribute("style", "dispslay: all;");
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

let count_hop = 0

function showMembers(id){
    let but = document.getElementById("show-members-"+id);
    let el = document.getElementById("members-list-"+id);
    if (el.style.display === 'none'){
        el.setAttribute("style", "display:all");
        but.textContent = "скрыть участников";
        but.setAttribute("style", "text-decoration: line-through")
    } else {
        el.setAttribute("style", "display:none");
        but.textContent = "показать участников";
        but.setAttribute("style", "text-decoration: underline")
    }
}