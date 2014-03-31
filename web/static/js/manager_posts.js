$(document).ready(function() {
    $('#posts tr:gt(0)').dblclick(function () {
        var id = $(this).index() + 1;
        var post_id = $(this).attr('post_id');
        var posting_status = $(this).attr('posting_status');

        PostManager.showUpdateDialog(post_id, posting_status);
    });
});

var PostManager = {
    /*
     * Добавить аккаунт
     */
    add: function(name, access_token) {
        $.ajax({
            url: '/manager/posts/add/',
            type: 'POST',
            data: {name: name, access_token: access_token},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#addPostError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#addPostError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Удалить выбранные аккаунты
     */
    remove: function() {
        // Составить список идентификаторов групп
        var posts = [];
        $('.post_select').filter(':checked').each(function() {
            posts.push($(this).attr('post_id'));
        });

        // Отправить запрос
        $.ajax({
            url: '/manager/posts/delete/',
            type: 'POST',
            data: {posts: posts},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#removePostsError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#removePostsError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Показать диалог добавления аккаунта
     */
    showAddDialog: function() {
        $('#addPostError').hide();
        $('#addPostIframe').attr('src', '/manager/posts/add/' + campaign_id);
        $('#addPostModal').modal('show');
    },

    showRemoveDialog: function() {
        $('#removePostsError').hide();
        $('#removePostsModal').modal('show');
    },

    showUpdateDialog: function(post_id, posting_status) {
        if(posting_status != 'waiting') {
            return;
        }
        $('#updatePostIframe').attr('src', '/manager/posts/update/' + post_id);
        $('#updatePostModal').modal('show');
    },

    toggleChecked: function() {
        var checked = $('#select_posts').is(':checked');
        $('.post_select').attr('checked', checked);
    }
}
