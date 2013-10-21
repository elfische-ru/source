
class window.UserInfo
    last_message_code = null

    constructor: (data) ->
        @container = data.container
        @log = $('<ul>').addClass 'log'
        @container.append @log

    add: (msg) ->
        @log.append($('<li>').html(msg))

    add_last: (message_code, msg) ->
        if message_code == @last_message_code
            @log.find('li:last-child').html(msg)
        else
            @add(msg)
            @last_message_code = message_code
