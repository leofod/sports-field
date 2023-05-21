$(document).ready(function () {
    var frm = $('#check-reg');
    $('#check-reg').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.redirect) {
                    window.location.href = "/";
                } else {
                    var change = document.getElementById('notice-check-reg');
                    change.setAttribute("style", "display:all");
                    if (response.no_empty){
                        document.getElementById("id_verification_code").value = '';
                        $("#notice-check-reg").html('Неправильный проверочный код.');
                    } else {
                        $("#notice-check-reg").html('Введите проверочный код.');
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

$(document).ready(function () {
    var frm = $('#resend');
    $('#resend').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.resend === true){
                    var change = document.getElementById('notice-check-reg');
                    change.setAttribute("style", "display:all");
                    $("#notice-check-reg").html('Вам на почту потворно выслан пароль.');
                } else {
                    var change = document.getElementById('notice-check-reg');
                    change.setAttribute("style", "display:all");
                    var ret_str = `Повторно отправить проверочный код можно будет в ` + response.resend +  `.`
                    $("#notice-check-reg").html(ret_str);
                }
                console.log(response.ans)
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
    var frm = $('#delete');
    $('#delete').submit(function () {
        $.ajax({
            data: $(this).serialize(), 
            type: $(this).attr('method'), 
            url: frm.attr('action'),
            success: function (response) {
                if (response.redirect) {
                    window.location.href = "/reg";
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