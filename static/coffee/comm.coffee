
class window.Comm
    constructor: ->
        @dispathers = {}
        @channel = new goog.appengine.Channel JS_DATA.user_tocken
        @socket = @channel.open()
        # @socket.onopen = => @sent('state', 'chat': 'opened')
        @socket.onmessage = (evt) =>
            data = JSON.parse(evt.data)
            for name, dispath of @dispathers
                dispath(data)

    sent: (action, data) ->
        $.ajax
            type: 'POST'
            url: '/api/' + action
            data: data

    onmessage: (name, dispath) ->
        @dispathers[name] = dispath
