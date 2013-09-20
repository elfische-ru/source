
class Comm
    constructor: ->
        @dispathers = []
        @channel = new goog.appengine.Channel JS_DATA.user_tocken
        @socket = @channel.open()
        # @socket.onopen = => @sent('state', 'chat': 'opened')
        @socket.onmessage = (evt) =>
            data = JSON.parse(evt.data)
            for dispath in @dispathers
                dispath(data)

    sent: (action, data) ->
        $.ajax
            type: 'POST'
            url: '/api/' + action
            data: data

    onmessage: (dispath) ->
        @dispathers.push dispath

class Chat
    constructor: ->
        @content    = $('<ul>').addClass('content')
        @chat_input = $('.chat .input-box input')
        @comm       = new Comm()

        @comm.onmessage @onmessage.bind this

        @add_messages(JS_DATA.last_messages)
        @init_sent()

        $('.chat .content-wrapper').append(@content)

        $('body .chat .sent').click =>
            @comm.sent 'chat_message', msg: @chat_input.val()
            @chat_input.val('').focus()

        if ! JS_DATA.is_mobile
            setTimeout(
                =>
                    @chat_input.focus()
                    $.injectCSS
                        '.chat .input-box input':
                            'animation': 'ma_ab1 .5s',
                            '-webkit-animation': 'ma_ab1 .5s'
                400
            )

        @show_users_count JS_DATA.users_count

    highlight: ->
        @chat_input.toggleClass('animate')

    focus: ->
        @chat_input.focus()
        @highlight()

    init_sent: ->
        @chat_input
            .keydown (evt) =>
                if evt.keyCode == 13
                    target = $(evt.currentTarget)
                    @comm.sent 'chat_message', msg: target.val()
                    target.val ''

    show_users_count: (count) ->
            $('.chat .chat-info dd').text(count)

    onmessage: (data) ->
        if data.add_message isnt undefined
            @add_messages([data.add_message])
        else if data.users_count isnt undefined
            @show_users_count data.users_count
        else if data.check_user isnt undefined
            @comm.sent 'check_user_live', user_id: JS_DATA.user_id

    add_messages: (messages) ->
        add_items = []
        for item in messages
            add_items.push($('<li>').append(item.msg))
        add_items.reverse()
        @content.append(add_items)


$(document).ready ->

        new Chat()

        #=======================================================================

        show_size = (width) -> $('#test').text width
        set_text_size = ->
            $('.info .cover-wrapper .summary').css({
                fontSize: ($('.info .cover-wrapper .cover').width() / 200) + 'rem'
            })


        set_text_size()
        # show_size($(this).width())

        $(window).resize ->
            # show_size($(this).width())
            set_text_size()


        if JS_DATA.is_mobile
            $('footer').insertAfter(".info")


