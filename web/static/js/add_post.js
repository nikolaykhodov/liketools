
var PostEditor = {
    add_photo_callback: null,
    add_group_callback: null,
    add_video_callback: null,

    groups: [],
    pic_medias: [],
    doc_medias: [],

    onChange: function() {},

    /*
     * Инициализация редактора постов
     *
     * @param {function() {} } функция обработчик, вызываемый при изменении параметров поста
     */
    init: function(onChange) {
        this.onChange = onChange;

        $('#page_add_media span').mouseover(function() {
            $('#add_media_menu').show();
        });

        $('.add_media_rows').mouseleave(function(event) {
            $('#add_media_menu').hide();
        });

        // Уведомляем об изменениях
        $('#post_field').change(onChange).keyup(onChange);
        $('#post_interval_value').change(onChange).keyup(onChange);
        $('#delete_after_posting_value').change(onChange).keyup(onChange);
        $('#post_schedule_timestamp').change(onChange).keyup(onChange);
        $('#delete_schedule_timestamp').change(onChange).keyup(onChange);

        $('.choose_close').click(function() {
            PostEditor.hide_dialog($(this).attr('dialog'));
        });

        // Прячем все панельки настройки режимов размещения/удаления
        $('.vk .post_mode').hide();

        // Полям выбора даты/времени подключаем всплывающий календарь
        $('.timestamp').datetimepicker({
            dateFormat: 'dd.mm.yy',
            timeFormat: 'hh:mm'
        });

        // Клик по фону диалога прячет его
        $('.popup_box_container').click(function(event) {
            event.stopPropagation();
        });

        $('#dialogs').click(function() {
            // Не прятать системные диалоги
            if($('#access_token_chooser,#submit_post_dialog').is(':visible')) {
                return;
            }

            $(this).hide().find('.popup_box_container').hide();
        });

        //this.checkVkToken();
    },

    /*
     * Переключение между режимами удаления поста
     *
     * @param {string} mode Название режима для удаления. Если не указано,
     *                      то берет текущее значение из #when_to_post_mode
     */
    changeWhenToPost: function(mode) {
        mode = mode || $('#when_to_post_mode option:selected').val();
        $('.when_to_post').hide();
        $('#post_' + mode).show();

        // Уведомляем об изменениях
        this.onChange();
    },

    /*
     *
     */
    changeWhenToDelete: function(mode) {
        mode = mode || $('#when_to_delete_mode option:selected').val();
        $('.when_to_delete').hide();
        $('#delete_' + mode).show();

        // Уведомляем об изменениях
        this.onChange();
    },

    changePostingAccount: function() {
        // Уведомляем об измениях
        this.onChange();
    },

    changePostingMode: function() {
        // Уведомляем об измениях
        this.onChange();
    },


    /*
     *
     */
    changeToken: function() {
        $('#access_token_chooser .error .description').html('');
        PostEditor.show_dialog('access_token_chooser', true);
        $('#access_token').focus();
    },

    changeAccount: function() {
        this.onChange();
    },

    /*
     *
     */
    show_dialog: function(dialog, canClose) {
        // Запретить прокрутку относительно страницы
        $('body').css({overflow: 'hidden'});

        // Показать диалог
        $('#dialogs').show();
        $('#' + dialog).show();

        // Разрешить ли пользователю закрытие диалога?
        if(typeof canClose == 'boolean') {
            if(canClose) {
                $('#' + dialog + ' .choose_close').show(); 
            } else {
                $('#' + dialog + ' .choose_close').hide(); 
            }
        }
    },

    /*
     *
     */
    hide_dialog: function(dialog) {
        // Спрятать диалог
        $('#dialogs').hide();
        $('#' + dialog).hide();

        // Вернуть прокрутку страницы
        $('body').css({overflow: 'auto'});
    },

    /*
     * Проверяет токен
     *
     * @param {string} token Токен для проверки. Если не указан, то берется из manager_options.access_token
     * @param {boolean} new_attempt Новая попытка сохранить токен: тогда токен сохраняется на сервере
     */
    checkVkToken: function(token, new_attempt) {
        if(token) { 
            // Если указана ссылка после авторизации https://oauth.vk.com/blank.html...
            var matches = token.match(/access_token=([a-z0-9]+)/);
            if(matches) {
                token = matches[1];
            }
        } else {
            token = manager_options.access_token;
        }

        VK.checkToken(token, function(err, callback) {
            if(err) {
                PostEditor.show_dialog('access_token_chooser');

                $('#access_token_chooser .error .description').html('Произошла ошибка: ' + err.toString());
                $('#access_token').
                    animate({backgroundColor: '#F2DEDE'}, 300).
                    animate({backgroundColor: '#FFFFFF'}, 300).
                    focus();
                return;
            }

            // Был обновлен токен
            if(new_attempt) {
                // Сохранить на сервер
                $.ajax({
                    url: '/keyvalue/set/',
                    type: 'POST', 
                    data: {access_token: token}
                });

                manager_options.access_token = token;
            }

            PostEditor.hide_dialog('access_token_chooser');
        });
    },

    /*
     *
     */
    format_duration: function(du) {
        var hours = parseInt(du / 3600);
        var minutes = parseInt((du - 3600 * hours) / 60)
        var seconds = du % 60;

        return (hours > 0 ? hours.zfill(2) + ':' : '') + minutes.zfill(2) + ':' + seconds.zfill(2);
    },

    /*
     * Проверяет, выбрала ли группа
     *
     * @param {Number} gid Номер группы
     */
    _group_isSelected: function(gid) {
        for(var i = 0; i < this.groups.length; i++) {
            if(this.groups[i].gid == gid && !this.groups[i].deleted)
                return true;
        }

        return false;
    },

    /*
     * Обертка для выбора группы
     */
    _group_onChoose: function() {
        var groups = [];
        $('#groups_chooser .group_selected').each(function() {
            groups.push({gid: $(this).attr('gid'), name: $(this).attr('name')});
        });
        this.hide_dialog('groups_chooser');
        this.add_group_callback(null, groups);
    },

    /*
     * Открывает диалог выбора групп и через callback возвращает номер группы
     *
     * @param {function(err, [{gid: ..., name: ...}, ...])} callback
     */
    _group_start: function(callback) {
        // Подготовливаем диалог
        PostEditor.show_dialog('groups_chooser');
        $('#groups_choose_rows').html('<div class="loader"></div>');
        
        // Запоминаем функцию обратного вызова
        this.add_group_callback = callback;
        
        var self = this;
        // Запрашиваем список групп, где пользователь - админ, и информацию о них
        VK.api('groups.getById', {gids: manager_groups.join(',')}, function(err, groups) {
            if(err || !groups)
                return callback(err, null);

            var html = "";

            // Код для отображения
            for(var i = 0; i < groups.length; i++) {
                if(self._group_isSelected(groups[i].gid))
                    continue;

                html += '<div class="groups_choose_row" gid="$gid$" name="$name$" onclick="$(this).toggleClass(\'group_selected\');"><img src="$img$" width="100" height="100"><span>$name$</span></div>'.
                            replace('$callback$', 'PostEditor._group_onChoose').
                            replace('$gid$', groups[i].gid).
                            replace('$img$', groups[i].photo_medium).
                            replace(/\$name\$/g, groups[i].name);


            }

            html += '<br class="clear">';

            $('#groups_choose_rows').html(html);
        });
    },

    /*
     * Обертка для выбора фотографии
     *
     * @param {Object} информация о выбранной фотографии
     */
    _photos_onChoose: function(photo) {
        this.hide_dialog('photos_chooser');
        this.add_photo_callback(null, photo);
    },
    /*
     * Подготавливает HTML-код для рендеринга диалога выбора фотографии
     *
     * @param {Array} массив фотографий
     * @param {string} callback название функции, используемой для выбора фотографии
     * @return {string} HTML-код
     */
    _photos_render: function(photos, callback) {
        var html = "";

        for(var i = 0; i < photos.length; i++) {
            html += ('<div class="photos_choose_row" onclick="$callback$({media_id: \'photo$oid$_$pid$\', thumbnail: \'$thumbnail$\'})">' +
                     '<a href="javascript:;"><img class="photo_row_img" src="$url$"></a>' + 
                     '</div>').
                        replace('$callback$', callback).
                        replace('$oid$', photos[i].owner_id).
                        replace('$pid$', photos[i].pid).
                        replace('$thumbnail$', photos[i].src_small).
                        replace('$url$', photos[i].src);
        }

        return html;
    },

    /*
     * Подгружает фотографии с определенным смещением (по умолчанию 0)
     *
     * @param {number} offset
     */
    _photos_preload: function(offset) {
        var count = 10;
        offset = offset || 0;

        $('#photos_choose_rows').append('<div class="loader"></div>');

        var self = this;
        VK.api('photos.getAll', {offset: offset, count: count}, function(err, photos) {
            // Убираем картинку прелоудера
            $('#photos_choose_rows').find('.loader').remove();

            // Обработка ошибок
            if(err || !photos) {
                return self.add_photo_callback(err, null);
            }

            // Добавить фотографии
            var html = PostEditor._photos_render(photos.slice(1), "PostEditor._photos_onChoose");
            $(html).insertBefore('#photos_choose_rows br');
            //$('#photos_choose_rows').html(html);

            // Есть ли еще фотографии?
            if(photos[0] > offset + photos.length - 1) {
                $('#photos_choose_more').css({display: 'block'}).attr('onclick', 'PostEditor._photos_preload(' + (offset + photos.length -1) + ')');
            } else {
                $('#photos_choose_more').hide();
            }
        });
    },

    /*
     * Очищает диалог выбора фотографий
     */
    _photos_clear: function() {
        $('#photos_choose_rows').html('<br class="clear">');
    },

    /*
     * Открывает диалог выбора фотографий и через callback возвращает информацию о фотке
     *
     * @param {function(err, {media_id: '...', thumbnail: '...'})} callback
     */
    _photos_start: function(callback) {
        // Подготовливаем диалог
        PostEditor.show_dialog('photos_chooser');

        // Запоминаем callback
        this.add_photo_callback = callback;

        this._photos_clear();
        this._photos_preload();
    },

    /*
     * Обертка для выбора видео
     *
     * @param {Object} video информация о выбранном видео
     */
    _video_onChoose: function(video) {
        this.hide_dialog('video_chooser');
        this.add_video_callback(null, video);
    },
    /*
     * Подготавливает HTML-код для рендеринга диалога выбора видео
     *
     * @param {Array} videos массив видео 
     * @param {string} callback название функции, используемой для выбора видео
     * @return {string} HTML-код
     */
    _video_render: function(videos, callback) {
        var html = "";

        for(var i = 0; i < videos.length; i++) {
            html += ('<div class="video_choose_row" onclick="$callback$({media_id: \'video$oid$_$vid$\', thumbnail: \'$thumbnail$\'})">' + 
                       '<div class="video_thumbnail">' + 
                         '<img src="$thumbnail$" width="130" height="98">' + 
                         '<span>$duration$</span>' + 
                       '</div>' + 
                       '<span>$title$</span>' + 
                     '</div>').
                        replace('$callback$', callback).
                        replace('$oid$', videos[i].owner_id).
                        replace('$vid$', videos[i].vid || videos[i].id).
                        replace(/\$thumbnail\$/g, videos[i].image || videos[i].image_medium).
                        replace('$title$', videos[i].title).
                        replace('$duration$', this.format_duration(videos[i].duration));
        }

        return html;
    },

    /*
     * Начинает поиск по видеозаписям. Если запрос не указан, то берется из поисковой строки
     *
     * @param {string} query
     */
    _video_search: function(query) {
        query = query || $('#video_search').val();
        this._video_preload(0, query);
    },

    /*
     * Подгружает список видео с определенного смещения
     *
     * @param {number} offset
     * @param {string} query
     */
    _video_preload: function(offset, query) {
        var count = 10;
        offset = offset || 0;
        query = query || '';

        // Начинаем поиск по видеозаписям?
        if(offset == 0) {
            this._video_clear();
        }

        // Если есть запрос, то надо вставить его в поисковую строку
        // и отобразить возврат к моим видеозаписям
        if(query) {
            $('#return_to_my_video').show();
            $('#video_search').val(query);
        } else {
            $('#return_to_my_video').hide();
            $('#video_search').val('');
        }

        // Показать прелоудер
        $('#video_choose_rows').append('<div class="loader"></div>');

        var method = query ? 'video.search' : 'video.get';

        var self = this;
        VK.api(method, {offset: offset, count: count, q: query}, function(err, videos) {
            // Убираем картинку прелоудера
            $('#video_choose_rows').find('.loader').remove();

            // Обработка ошибок
            if(err || !videos) {
                return self.add_video_callback(err, null);
            }

            // Если в режиме поиска, то надо исключить первый элемент (кол-во видео)
            if(typeof videos[0] == "number") {
                videos = videos.slice(1);
            }

            // Добавить видео
            var html = PostEditor._video_render(videos.slice(1), "PostEditor._video_onChoose");
            $(html).insertBefore('#video_choose_rows br');

            // Есть ли еще фотографии?
            //if(videos[0] > offset + videos.length - 1) {
            if(videos.length > 0) {
                $('#video_choose_more').css({display: 'block'}).attr('onclick', 'PostEditor._video_preload(' + (offset + videos.length) + ', "' + query + '");');
            } else {
                $('#video_choose_more').hide();
            }
        });
    },

    /*
     * Очищает список видеозаписей
     */
    _video_clear: function() {
        $('#video_choose_rows').html('<br clear="clear">');
    },

    /*
     * Очищает диалог выбора видео
     */
    _video_clear: function() {
        $('#video_choose_rows').html('<br class="clear">');
    },


    /*
     * Открывает диалог выбора фотографий и через callback возвращает информацию о фотке
     *
     * @param {function(err, {media_id: '...', thumbnail: '...'})} callback
     */
    _video_start: function(callback) {
        // Подготовливаем диалог
        PostEditor.show_dialog('video_chooser');

        // Запоминаем callback
        this.add_video_callback = callback;

        this._video_clear();
        this._video_preload();
    },

    _audio_onChoose: function(audio) {
        this.hide_dialog('audio_chooser');
        this.add_audio_callback(null, audio);
    },

    /*
     * Рисует список аудиозаписей
     *
     * @param {Array} audios аудиозаписи
     * @param {string} callback название функции для обработки выбора
     */
    _audio_render: function(audios, callback) {
        var html = "";

        for(var  i = 0; i < audios.length; i++) {
            html += ('<div class="audio_choose_row" onclick="$callback$({media_id: \'audio$oid$_$aid$\', title: \'$media_title$\'});">' + 
                       '<div class="song">' + 
                          '<b class="performer" onclick="PostEditor._audio_search(\'$performer$\'); event.stopPropagation();">$performer$</b> - $title$' + 
                        '</div>' + 
                        '<div class="duration">$duration$</div>' + 
                        '<br class="clear">' + 
                     '</div>').replace('$callback$', callback).
                        replace('$oid$', audios[i].owner_id).
                        replace('$aid$', audios[i].aid).
                        replace('$media_title$', '<b>' + audios[i].artist + '</b> - ' + audios[i].title).
                        replace('$title$', audios[i].title).
                        replace(/\$performer\$/g, audios[i].artist).
                        replace('$duration$', this.format_duration(audios[i].duration));
        }

        return html;
    },

    /*
     * Начинает поиск аудиозаписей по запросу. Если запрос не указан, то он берется из поисковой строки.
     *
     * @param {string} query
     */
    _audio_search: function(query) {
        query = query || $('#audio_search').val();
        this._audio_preload(0, query);
    },

    /*
     * Подгружает список аудиозаписей с определенного смещения и поисковым запросом
     * 
     * @param {number} offset
     * @param {string} query
     */
    _audio_preload: function(offset, query) {
        // Настройки
        var count = 10;
        offset = offset || 0;
        query = query || '';

        // Начинаем поиск по аудиозаписям?
        if(offset == 0) {
            this._audio_clear();
        }

        // Если есть запрос, то вставить в поисковую строку
        if(query) {
            $('#return_to_my_audio').show();
            $('#audio_search').val(query);
        } else {
            $('#return_to_my_audio').hide();
            $('#audio_search').val('');
        }

        
        // Показать прелоудер
        $('#audio_choose_rows').append('<div class="loader"></div>');

        // Выбрать метод
        var method = query ? 'audio.search' : 'audio.get';

        var self = this;
        VK.api(method, {offset: offset, count: count, q: query}, function(err, audios) {
            // Убираем картинку прелоудера
            $('#audio_choose_rows').find('.loader').remove();

            // Обработка ошибок
            if(err || !audios) {
                return self.add_audio_callback(err, null);
            }

            // Если в режиме поиска, то надо исключить первый элемент
            if(typeof audios[0] == 'number') {
                audios = audios.slice(1);
            }

            // Добавить аудио
            var html = PostEditor._audio_render(audios, "PostEditor._audio_onChoose");
            $('#audio_choose_rows').append(html);
            
            if(audios.length > 0) 
                $('#audio_choose_more').css({display: 'block'}).attr('onclick', 'PostEditor._audio_preload(' + (offset + audios.length) + ', "' + query + '")');
            else
                $('#audio_choose_more').hide();
        });
    },

    /*
     * Очишает список аудиозаписей
     */
    _audio_clear: function() {
        $('#audio_choose_rows').html('<br class="clear">');
    },

    /*
     * Открывает диалог выбора аудио
     *
     * @param {function(err, {media_id: '...', title: '...'})} callback
     */
    _audio_start: function(callback) {
        PostEditor.show_dialog('audio_chooser');

        this.add_audio_callback = callback;

        this._audio_clear();
        this._audio_preload();
    },

    /*
     * Обрабатывает изменение позиции прикрепленного pic-media
     */
    _onPicMediaChanged: function() {
        this.onChange();
    },
    /*
     * Добавляет прикрепление c картинкой в список
     *
     * @param {string} media_id название медиа
     * @param {string) thumbnail ссылка на миниатюру
     */
    addPicMedia: function(media_id, thumbnail) {
        var html = ('<div class="media page_preview_photo_wrap" media_id="$media_id$">' +
                    '  <div class="page_preview_photo">' + 
                    '    <img src="$thumbnail$" width="75" height="56" onclick="PostEditor.preview(\'$media_id$\');">' + 
                    '  </div>' + 
                    '  <div class="page_media_x_wrap" tootltip="Не прикреплять" onclick="PostEditor.deleteMedia(this);">' + 
                    '    <div class="page_media_x"></div>' + 
                    '  </div>' + 
                    '</div>').replace(/\$media_id\$/g, media_id).replace('$thumbnail$', thumbnail);
        $('#page_pics_preview').append(html);

        // Сохранить информацию о прикреплении
        this.pic_medias.push({media_id: media_id, thumbnail: thumbnail, deleted: false}); 

        $('#page_pics_preview').sortable({
            stop: function() { PostEditor._onPicMediaChanged(); }
        });
    },

    /*
     * Добавляет прикрепление с текстом
     *
     * @param {string} media_id идентификатор прикрепления
     * @param {string} media_title название прикрепления
     */
    addDocMedia: function(media_id, media_title) {
        var html = ('<div class="page_preview_audio_wrap clear_fix media" media_id="$media_id$">' + 
                    '  <div class="audio">' + 
                    '    <div class="media_audio_icon"></div>' + 
                    '      <span>$title$</span>' + 
                    '    </div>' + 
                    '   <div class="page_docs_x_wrap" tootltip="Не прикреплять" onclick="PostEditor.deleteMedia(this);">' + 
                    '     <div class="page_docs_x"></div>' + 
                    '   </div>' + 
                    '</div>').replace('$media_id$', media_id).replace('$title$', media_title);

        $('#page_docs_preview').append(html);

        // Сохранить информацию о прикреплении
        this.doc_medias.push({media_id: media_id, media_title: media_title, deleted: false});
    },


    /*
     * Добавляет группу в список
     *
     * @param {number} gid
     * @param {string} name
     */
    addGroupToList: function(gid, name) {
        // Запретить повторные добавления
        if($('#group_' + gid).length > 0) {
            return;
        }

        var html = '<div id="group_' + gid + '" gid="' + gid + '" class="group_link" style="cursor: pointer;"><span>' + name + '</span> <div class="page_docs_x_wrap" onclick="PostEditor.deleteGroup(this);"></div></div>';
        $(html).insertBefore('#add_group');
        
        // Сохранить
        this.groups.push({gid: gid, name: name, deleted: false});
    },

    /*
     * Удаляет приложения из списка
     */
    deleteMedia: function(el) {
        var media_id = $(el).parent().attr('media_id');
        if(!media_id) {
            return;
        }

        // Выбираем подходящий список с приложениями
        var medias = null;
        if(media_id.indexOf('audio') >= 0)
            medias = this.doc_medias;
        else
            medias = this.pic_medias;

        // Помечаем все приложения (т.к. может быть добавлено неоднократно) как удаленные
        for(var  i = 0; i < medias.length; i++) {
            if(medias[i].media_id == media_id)
                medias[i].deleted = true;
        }

        $(el).parent().remove();

        // Уведомляем об изменениях
        this.onChange();
    },

    /*
     * Удаляет группу из списка
     *
     * @param {$('.page_docs_x_wrap')} el
     */
    deleteGroup: function(el){
        var gid = parseInt($(el).parent().attr('gid'));
        if(!gid) {
            return;
        }

        for(var i = 0; i < this.groups.length; i++) {
            if(this.groups[i].gid == gid)
                this.groups[i].deleted = true;
        }

        $(el).parent().remove();

        this.onChange();
    },

    /*
     * Инциирует добавление группы
     */
    addGroup: function() {
        var self = this;

        this._group_start(function(err, groups) {
            if(err || !groups) {
                return alert(err);
            }

            for(var i = 0; i < groups.length; i++) {
                var group = groups[i];
                PostEditor.addGroupToList(group.gid, group.name);
            }

            // Уведомляем об изменениях
            self.onChange();
        });
    },

    /*
     * Инициирует добавление фотографии
     */
    addPhoto: function() {
        // Спрятать меню
        $('#add_media_menu').hide();

        var self = this;
        this._photos_start(function(err, photo) {
            if(err || !photo) {
                return alert(err);
            }

            PostEditor.addPicMedia(photo.media_id, photo.thumbnail);
            // Уведомляем об изменениях
            self.onChange();
        });
    },

    /*
     * Инициирует добавление видео
     */
    addVideo: function() {
        // Спрятать меню
        $('#add_media_menu').hide();

        var self = this;
        this._video_start(function(err, video) {
            if(err || !video) {
                return alert(err);
            }

            PostEditor.addPicMedia(video.media_id, video.thumbnail);
            // Уведомляем об изменениях
            self.onChange();
        });
    },

    /*
     * Инициирует добавление аудио
     */
    addAudio: function() {
        // Спрятать меню
        $('#add_media_menu').hide();

        var self = this;
        this._audio_start(function(err, audio) {
            if(err || !audio) {
                return alert(err);
            }
            PostEditor.addDocMedia(audio.media_id, audio.title);
            // Уведомляем об изменениях
            self.onChange();
        });
    },


    /*
     * Задает значения для фейковых и реального select'ов
     */
    _select_val: function(id, val) {
        var real_sel = $('#' + id);
        var fake_sel = real_sel.prev();
        var text = fake_sel.find('.select_option').filter(function() { return $(this).attr('value') == val; }).html();

        real_sel.val(val);
        fake_sel.find('.selected-text').html(text);
    },

    /*
     * Возврашает состояние рекдактор
     */
    save: function() {
        function filter(medias) {
            var filtered_medias = [];

            for(var i = 0; i < medias.length; i++) {
                if(medias[i].deleted == false)
                    filtered_medias.push(medias[i]);
            }

            return filtered_medias;
        }
        function sort(medias, els) {
            var new_medias = [];

            // Пройти по списку элементов
            for(var i = 0; i < els.length; i++) {
                var media_id = $(els[i]).attr('media_id');

                // Найти приложение с текущим media_id
                var media = null;
                for(var j = 0; j < medias.length; j++) {
                    if(medias[j].media_id == media_id)
                        media = medias[j];
                }

                // Вставить его в массив
                if(media)
                    new_medias.push(media);
            }
            // Вернуть список приложений в том порядке, как в редакторе постов
            return new_medias;
        }
        return {
            doc_medias: filter(this.doc_medias),
            pic_medias: sort(filter(this.pic_medias), $('#page_pics_preview .media')),
            groups: filter(this.groups),
            text: $('#post_field').val(),

            when_to_post_mode: $('#when_to_post_mode').val(),
            when_to_delete_mode: $('#when_to_delete_mode').val(),

            post_interval: {
                value: $('#post_interval_value').val(),
                step: $('#post_interval_step').val()
            },

            post_schedule_timestamp: $('#post_schedule_timestamp').val(),

            delete_after_posting: {
                value: $('#delete_after_posting_value').val(),
                step: $('#delete_after_posting_step').val()
            },

            delete_schedule_timestamp: $('#delete_schedule_timestamp').val(),
            
            posting_account: $('#posting_account').val(),

            posting_mode: $('#posting_mode').val()
        };
    }, 

    /*
     * Восстанавливает состояние редактора
     *
     * @param {object} obj состояние редактора
     */
    restore: function(obj) {
        var self = this;
        $.each(obj.doc_medias, function() {
            self.addDocMedia(this.media_id, this.media_title);
        });
        $.each(obj.pic_medias, function() {
            self.addPicMedia(this.media_id, this.thumbnail);
        });
        $.each(obj.groups, function() {
            self.addGroupToList(this.gid, this.name);
        });

        $('#post_field').val(obj.text);

        // when_to_post_mode
        this._select_val('when_to_post_mode', obj.when_to_post_mode);
        this.changeWhenToPost(obj.when_to_post_mode);

        // when_to_delete_mode
        this._select_val('when_to_delete_mode', obj.when_to_delete_mode);
        this.changeWhenToDelete(obj.when_to_delete_mode);

        // post_interval
        $('#post_interval_value').val(obj.post_interval.value);
        this._select_val('post_interval_step', obj.post_interval.step);

        // post_schedule_timestamp
        $('#post_schedule_timestamp').val(obj.post_schedule_timestamp);

        // delete_after_posting
        $('#delete_after_posting_value').val(obj.delete_after_posting.value);
        this._select_val('delete_after_posting_step', obj.delete_after_posting.step);

        // delete_schedule_timestamp
        $("#delete_schedule_timestamp").val(obj.delete_schedule_timestamp);

        // posting account
        this._select_val('posting_account', obj.posting_account);

        // posting_mode
        this._select_val('posting_mode', obj.posting_mode);
    }, 

    /*
     * Открывает предпросмотр фотографии или видео
     *
     * @param {string} media photoXXX_XXX или videoXXX_XXX
     */
    preview: function(media) {
        var is_photo = media.indexOf('photo') == 0;
        var is_video = media.indexOf('video') == 0;
        var prefix = is_photo ? 'photo' : 'video';

        $('#' + prefix + '_preview_wrap').html('<div class="loader"></div>');
        this.show_dialog(prefix + '_preview');

        if(is_photo) {
            VK.api('photos.getById', {photos: media.replace('photo', '')}, function(err, photos) {
                if(err || !photos) {
                    alert(err);
                    PostEditor.hide_dialog('photo_preview');
                }

                // Найти URL самой большей фотки
                var src = photos[0].src_xxbig || photos[0].src_xbig || photos[0].src_big || photos[0].src;

                var img = new Image();
                img.onload = function() {
                    var width = Math.min(592, img.width);

                    $('#photo_preview_wrap').html('<img src="$src$" width="$width$" height="">'.
                        replace('$src$', src).
                        replace('$width$', width)
                    );
                }
                img.src = src;
            });
        } else if(is_video) {
            VK.api('video.get', {videos: media.replace('video', '')}, function(err, videos) {
                if(err || !videos) {
                    alert(err);
                    PostEditor.hide_dialog('video_preview');
                }

                var url = videos[1].player;

                $('#video_preview_wrap').html('<iframe src="$url$" frameborder=0 width=590 height=320></iframe>'.replace("$url$", url));
            });
        } else {
            this.hide_dialog(prefix + '_preview');
        }

    },

    /*
     * Отправляет запрос на добавление постов в очередь
     *
     * @param {function(['err1', 'err2', ...]} Callback
     */
    submit: function(callback) {
        function format_param(ar, key) {
            var attach = [];
            for(var i = 0; i < ar.length; i++) {
                attach.push(ar[i][key]);
            }
            return attach.join(',');
        }
        // Подготовить данные для отправки
        var state = this.save();
        state.attachments = [format_param(state.pic_medias, 'media_id'), format_param(state.doc_medias, 'media_id')].join(',');
        state.groups = format_param(state.groups, 'gid');
        state.campaign = campaign_id;
        state.editor_data = JSON.stringify(this.save());

        // Добавить данные об антикапче
        $.extend(state, manager_options);
        
        // Подготовить диалог
        $('#submit_post_wrap').html('<div class="loader"></div>');
        $('#submit_post_button_wrap').hide();
        this.show_dialog('submit_post_dialog', false);


        var submit_url = typeof is_updating == 'undefined' || !is_updating ? '/manager/posts/submit/' : '/manager/posts/update/:id/'.replace(':id', post_id);
        // Отправить запрос на добавление постов(-а) в очередь
        $.ajax({
            type: 'POST',
            url: submit_url,
            data: state,
            dataType: 'json',
            success: function(response) {
                // Показать кнопку Закрыть после обработки запроса на сервер
                $('#submit_post_button_wrap').show();

                // При наличии ошибок отобразить их список
                if(!response.error) {
                    $('#submit_post_wrap').html('<div class="success">Добавлание постов(-а) успешно выполнено. После нажатия кнопки <b>Закрыть</b> форма будет очищена, но будет сохранен список групп.</div><br class="clear"/>');

                    // После закрытия диалоги сохранить только группы  и перегрузить страницу
                    $("#submit_post_close").attr("onclick", "PostEditor.reloadAfterPosting();");
                } else {
                    var html = '<div class="error"><ul>';
                    for(var i = 0; i < response.errors.length; i++) {
                        html += '<li>error</li>'.replace('error', response.errors[i]);
                    }
                    html += '</div><br style="clear"/>';

                    $('#submit_post_wrap').html(html);
                }
            },
            error: function() {
                // Показать кнопку Закрыть после обработки запроса на сервер
                $('#submit_post_button_wrap').show();

                $('#submit_post_wrap').html('<div class="error">Произошла техническая ошибка при отправке запроса.</div><br class="clear"/>');
            }
        });
    },

    /*
     * Оставляет только группы и перегружает страницу
     */
    reloadAfterPosting: function() {
        this.pic_medias = [];
        this.doc_medias = [];

        $('#post_field').val('');

        this.onChange();

        // Reload top frame
        top.location.replace('/manager/posts/' + campaign_id + '/' );
    }
}

$(document).ready(function() {


    // Сохраняем в localStorage информацию о состоянии редактора при любом изменении 
    PostEditor.init(function() {
        localStorage.setItem('post_editor_data', JSON.stringify(PostEditor.save()));
        $.cookie('post_editor_data', JSON.stringify(PostEditor.save()));
    });

    // Пытаемся восстановить состояние редактора при загрузке
    var data = null;
    if(typeof editor_data == 'undefined') {
        try {
            var data = JSON.parse(localStorage.getItem('post_editor_data'));
        } catch(e) {}
    } else {
        data = editor_data;
    }
    PostEditor.restore(data);

	/* Непонятный код =) */
	$('.select_simulator').live('click', function() {
		$('.select_simulator').removeClass('act');
		$(this).addClass('act');

		if ($(this).children('.select_options').is(':visible')) {
			$('.select_options').hide();
		} else {
			$('.select_options').hide();
			$(this).children('.select_options').show();
		}
	});
	
	var selenter = false;
	$('.select_simulator').live('mouseenter', function() {
		selenter = true;
	});
	$('.select_simulator').live('mouseleave', function() {
		selenter = false;
	});
	
	$('.select_option').live('click', function() {
		var text = $(this).html();
		$(this).parent('.select_options').parent('.select_simulator').children('.select_selected').children('.selected-text').html(text);

		var val = $(this).attr('value');
		val = typeof(val) != 'undefined' ? val : text;
	
		$(this).parent('.select_options').parent('.select_simulator').parent('.select_wrap').children('select').children('option').removeAttr('selected').each(function() {
			if ($(this).val() == val) {
				$(this).attr('selected', 'select');
			}
		});
		PostEditor.changeWhenToPost();
		PostEditor.changeWhenToDelete();
        PostEditor.changePostingAccount();        
		selenter = false;
	});
	
	$(document).click(function() {
		if (!selenter) {
			$('.select_options').hide();
			$('.select_simulator').removeClass('act');
		}
	});

});
Number.prototype.zfill = function(len) {
    var val = this.toString();
    if (val.length < len) {
        for(var i = 0; i < len - val.length; i++)
            val = '0' + val;
    }
    return val;
};
