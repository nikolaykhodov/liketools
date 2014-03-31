var Options = {
    list_opts: ['antigate_key', 'posting_delay', 'captcha_attempts', 'captcha_attempts_delay'],

    save: function() {
        var data = {};
        for(var i = 0; i < this.list_opts.length; i++) {
            data[this.list_opts[i]] = $('#' + this.list_opts[i]).val();
        }

        // Отправить данные на сохранение
        $.ajax({
            url: '/social_auth/keyvalue_set/', 
            type: 'POST',
            data: data,
            dataType: 'json'
        }).done(function() {
            $('#optionsSaveSuccess').show();
            setTimeout(function() {
                $('#optionsSaveSuccess').hide();
            }, 2500);
        }).fail(function() {
            $('#optionsSaveFail').show();
            setTimeout(function() {
                $('#optionsSaveFail').hide();
            }, 2500);
        });
    }
};
