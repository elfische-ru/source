
class window.Comm
    retry_number: 0

    constructor: ->
        @dispathers = {}
        @open_channel()

    open_channel: ->
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
            @new_connection_delay()


    sent: (action, data) ->
        data.user_tocken = JS_DATA.user_tocken
        $.ajax
            type: 'POST'
            url: '/api/' + action
            data: data

    onmessage: (name, dispath) ->
        @dispathers[name] = dispath

    set_new_data: (data) ->
        JS_DATA.user_tocken = data.tocken
        JS_DATA.stream_user_id = data.stream_user_id
        @open_channel()

    new_connection_delay: ->
        setTimeout(
            @new_connection.bind(this),
            1000
        )

    new_connection: ->
        window.user_info.add_last(
            'new_connection',
            gettext('Устанавливается новое соединение, попытка: {0}')
                .format(@retry_number)
        )
        $.ajax
            type: 'POST'
            url: '/api/new_connection'
            dataType: 'json'
            error: (env) =>
                @retry_number++
                @new_connection_delay()
            success: (data) =>
                @retry_number = 0
                @set_new_data(data)
