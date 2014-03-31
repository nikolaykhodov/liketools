$(document).ready(function() {
    $('#accounts tr:gt(0)').dblclick(function () {
        var id = $(this).index() + 1;
        var account_id = $(this).attr('account_id');
        var login = $('#accounts tr:eq(' + id + ') td:eq(1)').text();
        var token = $('#accounts tr:eq(' + id + ') td:eq(2)').text();

        AccountManager.showUpdateDialog(account_id, login, token);
    });
});

var AccountManager = {
    /*
     * Добавить аккаунт
     */
    add: function(name, access_token) {
        $.ajax({
            url: '/manager/accounts/add/',
            type: 'POST',
            data: {name: name, access_token: access_token},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#addAccountError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#addAccountError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Удалить выбранные аккаунты
     */
    remove: function() {
        // Составить список идентификаторов групп
        var accounts = [];
        $('.account_select').filter(':checked').each(function() {
            accounts.push($(this).attr('account_id'));
        });

        // Отправить запрос
        $.ajax({
            url: '/manager/accounts/delete/',
            type: 'POST',
            data: {ids: accounts},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#removeAccountsError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#removeAccountsError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    update: function(login, token) {
        // Отправить запрос
        $.ajax({
            url: '/manager/accounts/update/',
            type: 'POST',
            data: {account_id: this.update_account_id, name: login, access_token: token},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#updateAccountError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#updateAccountError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Показать диалог добавления аккаунта
     */
    showAddDialog: function() {
        $('#addAccountError').hide();
        $('#addAccountModal').modal('show');
    },

    showRemoveDialog: function() {
        var quantity = $('.account_select').filter(':checked').length;

        $('#removeAccountCounter').html(quantity);
        $('#removeAccountsError').hide();
        $('#removeAccountsModal').modal('show');
    },

    showUpdateDialog: function(account_id, login, token) {
        $('#updateAccountError').hide();
        $('#updateAccountLogin').val(login);
        $('#updateAccountModal').modal('show');

        this.update_account_id = account_id;
    },

    toggleChecked: function() {
        var checked = $('#select_accounts').is(':checked');
        $('.account_select').attr('checked', checked);
    }
};
