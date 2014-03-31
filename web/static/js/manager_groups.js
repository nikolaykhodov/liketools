$(document).ready(function() {
    $('#groups tr').dblclick(function () {
        var id = $(this).index() + 1;
        var GroupName = $('#groups tr:eq(' + id + ') td:eq(1)').text().split('(');
        var GroupNumber = 'I dont know...'
        var GroupLink = GroupName[1].split(')')[0];

        $('#groupModal #myModalLabel').text(GroupName[0]);
        $('#groupModal #inputGroupName').val(GroupName[0]);
        $('#groupModal #inputGroupNumber').val(GroupNumber);
        $('#groupModal #inputGroupLink').val(GroupLink);
        $('#groupModal').modal('show')
    });
});

var GroupManager = {
    /*
     * Добавить группу по ссылке
     *
     * @param {string} link 
     */
    add: function(link) {
        $.ajax({
            url: '/manager/groups/add/',
            type: 'POST',
            data: {link: link},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#addGroupError').show().html(data.err_desc);
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#addGroupError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Удалить отмеченные группы
     */
    remove: function() {
        // Составить массив номеров выбранных групп
        var gids = [];
        $('.group_select').filter(':checked').each(function() {
            gids.push($(this).attr('gid'));
        });

        // Отправить запрос на удаление
        $.ajax({
            url: '/manager/groups/delete/',
            type: 'POST',
            data: {groups: gids},
            dataType: 'json'
        }).done(function(data) {
            if(data.error) {
                $('#removeGroupsError').show().html(data.err_desc);
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#removeGroupsError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Импортировать группы пользователя
     */
    import: function() {
        // Отправить запрос на импорт групп пользователя
        $.ajax({
            url: '/manager/groups/import/',
            type: 'POST',
            dataType: 'json'
        }).done(function(data) {
            if(data.error) {
                $('#importGroupsError').show().html(data.err_desc);
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#importGroupsError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Показать диалог добавления группы
     */
    showAddDialog: function(callback) {
        $('#addGroupError').hide();
        $('#addGroupModal').modal('show');
    },

    /*
     * Показать диалог удаления групп
     */
    showRemoveDialog: function(callback) {
        $('#removeGroupsError').hide();
        $('#removeGroupsModal').modal('show');
    },

    /*
     * Показать диалог импорта групп
     */
    showImportDialog: function(callback) {
        // Спрятать сообщение об ошибке
        $('#importGroupsError').hide();
        // Показать загрузку количества групп
        $('#importGroupsCounter img').show();
        $('#importGroupsCounter span').hide().removeClass('label-warning label-success');
        
        // Показать диалог
        $('#importGroupsModal').modal('show');

        // Запустить запрос количества импортируемых групп
        $.ajax({
            url: '/manager/groups/import/count/',
            type: 'POST',
            dataType: 'json'
        }).done(function(data) {
            // Спрятать картинку
            $('#importGroupsCounter img').hide();
            
            // Либо показать соощение об ошибке, или показать количество групп
            if(data.error) {
                // Предложить переавторизоваться,
                // т.к. самая вероятная причина - истечение срока действие токена или его отзыв
                $('#importGroupsCounter span').show().addClass('label-warning').html('Ошибка! <a href="' + data.auth_url + '">Переавторизоваться!</a>');
            } else {
                $('#importGroupsCounter span').show().addClass('label-success').html(data.count);
            }
        }).fail(function() {
            // Спрятать картинку
            $('#importGroupsCounter img').hide();
            // Отобразить сообщение об ошибке
            $('#importGroupsCounter span').show().addClass('label-warning').html('Ошибка!');
        });
    },

    /*
     * Выбрать/не выбрать все группы
     */
    toggleChecked: function() {
        var checked = $('#select_groups').is(':checked');
        $('.group_select').attr('checked', checked);
    }
};
