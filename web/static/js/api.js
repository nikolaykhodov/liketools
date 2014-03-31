/*
 Создает обертки, пригодные для JSONP-коммуникации, над произвольными функциями.
*/
var Callbacks = {
    handlers: [],
    
    /*
      Возвращает текстовое имя обертки, например, Callbacks.handlers[123].
 
      Все параметры этой обертки будут переданы в функцию, над которой она 
      была создана.
      
      @param {function} func 
     */
    get: function (func) {
        // Новый индекс
        var index = Callbacks.handlers.length;
        
        // Обертка
        Callbacks.handlers[index] = function() {
            func.apply(null, Array.prototype.slice.call(arguments));
        };
        
        // Имя
        return 'Callbacks.handlers['+index+']';
    }
};

var VK = {
    PHOTO_PERM: 4, // маска на права доступа к фото
    AUDIO_PERM: 8,// маска на права доступа к аудио
    VIDEO_PERM: 16,// маска на права доступа к видео
    GROUP_PERM: 262144,// маска на права доступа к группам
    AD_PERM: 32768,// маска на права доступа к рекламному кабинету


    /*(
     Вызывает метод ВКонтатке API по протоколу JSONP.
     
     Если ответ от ВКонтате не поступит в течение 15 секунд,
     то будет вызван callback c err='timeout';
     
     @param {string} method Название метода
     @param {Object} params
     @param {function(err, response)} callback
    */
    api: function(method, params, callback) {
        // URL запроса
        var url = 'https://api.vk.com/method/'+method+'?';
        if(!params) 
            params = {};

        if (typeof params['access_token'] == 'undefined') 
            params['access_token'] = manager_options.access_token || $.cookie('access_token');
        
        // Добавить параметры к методу
        for(var param in params) {
            url += '&' + param + '=' + encodeURIComponent(params[param]);        
        }
        
        // Флаг для отслеживания таймаута
        var responsed = false;
        
        // Функция-обработчик ответа
        url += '&callback=' + Callbacks.get(function(answer) {
            // Если все гут?
            if(answer.response) {
                callback(null, answer.response);
            } else {
                // иначе ошибки :(
                var error_msg = answer.error.error_msg;
                if(error_msg.indexOf('revoke') >= 0 || error_msg.indexOf('expire') >= 0) {
                    if(confirm('Возможно, что ваш токен отозван или истек срок действия. Поэтому вам следует переавторизоваться через ВК. Переавторизоваться?')) {
                        top.location.replace(auth_url);
                        return;
                    }
                }
                callback(answer.error.error_msg, null);
            }
            responsed = true;
        });

        // Если нет ответа 15 секунд, то timeout
        setTimeout(function() {
            if(!responsed) {
                callback('timeout', null);    
            }
        }, 15000);
        
        // Инициировать запрос
        var script = document.createElement('script');
        script.src = url;    
        document.body.appendChild(script);
    },

    /*
     * Проверяет правильность токена
     *
     * @param {string} token токен
     * @param {function(err, valid)}
     */
    checkToken: function(token, callback) {
       this.api('getUserSettings', {access_token: token}, function(err, response) {
            if(err) {
                return callback(err, false);
            }
            return callback(null, true);
       });
    }
};
