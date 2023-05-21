$(document).ready(function () {
    var frm = $('#add-playground-form');
    $('#add-playground-form').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.ans){
                    window.location.href = "http://127.0.0.1:8000/";
                }else{
                    console.log(response.code);
                    if (response.code == 1 || response.code == 4){
                        $("#notice-add-playground").html("Выберите вид спорта");
                    } else if (response.code == 2){
                        $("#notice-add-playground").html("Заполните поле \"Адрес или ссылка\"");
                    } else if (response.code == 2){
                        $("#notice-add-playground").html("Выберите тип площадки");
                    } 
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
