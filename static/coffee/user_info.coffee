
class window.UserInfo
    constructor: (data) ->
        @container = data.container
        @log = $('<ul>').addClass 'log'
        @container.append @log

    add: (msg) ->
        @log.append($('<li>').html(msg))
