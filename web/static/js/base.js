$(document).ready(function() {
    var tokens = $('#current_time').attr('start').split(' ');
    for(var i = 0; i < tokens.length; i++) {
        tokens[i] = parseInt(tokens[i]);
    }
    var start_time = new Date(
        tokens[0], // Year
        tokens[1], // Month
        tokens[2], // Day
        tokens[3], // Hour
        tokens[4], // Minute
        tokens[5]  // Second
    ).getTime() / 1000;
       
    function serverTimeTick() {
        start_time += 1;
        var current_time = (new Date(start_time * 1000));
        $('#current_time_value').html("dd.mm.yyyy hh:ii:ss".
            replace('dd',   current_time.getDate().zfill(2)).
            replace('mm',  (current_time.getMonth() + 1).zfill(2)).
            replace('yyyy', current_time.getFullYear()).
            replace('hh',   current_time.getHours().zfill(2)).
            replace('ii',   current_time.getMinutes().zfill(2)).
            replace('ss',   current_time.getSeconds().zfill(2))
        );
    }
    setInterval(serverTimeTick, 1000);
    serverTimeTick();
});

Number.prototype.zfill = function(len) {
    var val = this.toString();
    if (val.length < len) {
        for(var i = 0; i < len - val.length; i++)
            val = '0' + val;
    }
    return val;
};

/*
 * Возвращает HTML-код для отображения списка ошибок в манагерском кабинете
 */
function renderErrorList(errors) {
    var html = '<ul class="error">';

    for(var i = 0; i < errors.length; i++) {
        html += '<li>error</li>'.replace('error', errors[i]);
    }

    html += '</ul>';

    return html;
}

