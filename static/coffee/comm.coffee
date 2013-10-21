
class window.Comm
    constructor: ->
        @dispathers = {}
        @channel = new goog.appengine.Channel JS_DATA.user_tocken
        window.user_info.add(
            gettext('Имя пользователя: {0}')
                .format('<strong>' + JS_DATA.stream_user_id + '<strong>')
        )

        @socket = @channel.open()

        @socket.onopen = (evt) =>
            window.user_info.add(gettext('Соединение установлено'))

        # @socket.onopen = => @sent('state', 'chat': 'opened')

        @socket.onmessage = (evt) =>
            data = JSON.parse(evt.data)
            for name, dispath of @dispathers
                dispath(data)

        @socket.onerror = (evt) =>
            window.user_info.add(gettext('Ошибка соединения'))

        @socket.onclose = (evt) =>
            window.user_info.add(gettext('Соединение закрыто'))


    sent: (action, data) ->
        data.user_tocken = JS_DATA.user_tocken
        $.ajax
            type: 'POST'
            url: '/api/' + action
            data: data

    onmessage: (name, dispath) ->
        @dispathers[name] = dispath
