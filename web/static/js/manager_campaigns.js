$(document).ready(function() {
    $('#campaigns tr:gt(0)').dblclick(function () {
        var id = $(this).index() + 1;
        var campaign_id = $(this).attr('campaign_id');
        var name = $('#campaigns tr:eq(' + id + ') td:eq(1)').text();

        CampaignManager.showUpdateDialog(campaign_id, name);
    });
});

var CampaignManager = {
    /*
     * Добавить аккаунт
     */
    add: function(name, access_token) {
        $.ajax({
            url: '/manager/campaigns/add/',
            type: 'POST',
            data: {name: name, access_token: access_token},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#addCampaignError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#addCampaignError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Удалить выбранные аккаунты
     */
    remove: function() {
        // Составить список идентификаторов групп
        var campaigns = [];
        $('.campaign_select').filter(':checked').each(function() {
            campaigns.push($(this).attr('campaign_id'));
        });

        // Отправить запрос
        $.ajax({
            url: '/manager/campaigns/delete/',
            type: 'POST',
            data: {ids: campaigns},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#removeCampaignsError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#removeCampaignsError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    update: function(login, token) {
        // Отправить запрос
        $.ajax({
            url: '/manager/campaigns/update/',
            type: 'POST',
            data: {campaign_id: this.update_campaign_id, name: login, access_token: token},
            dataType: 'json',
        }).done(function(data) {
            if(data.error) {
                $('#updateCampaignError').show().html(renderErrorList(data.errors));
            } else {
                window.location.replace('');
            }
        }).fail(function() {
            $('#updateCampaignError').show().html('Произошла техническая ошибка при обработке запроса');
        });
    },

    /*
     * Показать диалог добавления аккаунта
     */
    showAddDialog: function() {
        $('#addCampaignError').hide();
        $('#addCampaignModal').modal('show');
    },

    showRemoveDialog: function() {
        $('#removeCampaignsError').hide();
        $('#removeCampaignsModal').modal('show');
    },

    showUpdateDialog: function(campaign_id, name) {
        $('#updateCampaignError').hide();
        $('#updateCampaignName').val(name);
        $('#updateCampaignModal').modal('show');

        this.update_campaign_id = campaign_id;
    },

    toggleChecked: function() {
        var checked = $('#select_campaigns').is(':checked');
        $('.campaign_select').attr('checked', checked);
    }
}
