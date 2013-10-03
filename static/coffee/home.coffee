
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
            @comm.sent 'check_user_live', user_id: JS_DATA.stream_user_id

    check_message_length_async: (message) ->
        setTimeout(
            =>
                if ! @check_message_length(message)
                    @check_message_length_async(message)
            ,
            100
        )

    check_message_length: (message) ->
        parent = message.closest('li')
        if message.width() > 346
            fold = $('<span>')
                .addClass('fold-icon')
                .click( =>
                    parent.toggleClass('fold')
                )
            parent.append(fold)

    add_messages: (messages) ->
        add_items = []
        last_hidden_count = 0
        first_hidden = null
        for item in messages
            message = $('<span>').text(item.msg)
            control = $('<span>')
                .addClass('message-control')
                .append($('<span>').addClass('check'))
                .append($('<span>').addClass('hide'))
            @check_message_length_async(message)
            itemDom = $('<li>')
                .attr('id', 'message_id-' + item.id)
                .append(
                    $('<span>')
                        .addClass('message-wrapper')
                        .append(message)
                )
                .append(control)

            if item.hidden
                if last_hidden_count == 0
                    itemDom.addClass('first-hidden')
                    first_hidden = itemDom
                else
                    itemDom.addClass('hidden')
                last_hidden_count++
            else if last_hidden_count > 0
                first_hidden.append(
                    $('<span>')
                        .addClass('hidden-count')
                        .append(
                            $('<span>').text(
                                ngettext(
                                    'Скрыто {0} сообщение',
                                    '',
                                    last_hidden_count
                                ).format(last_hidden_count)
                            )
                        )
                )
                last_hidden_count = 0
                first_hidden = null

            @init_message(itemDom)
            add_items.push(itemDom)
        add_items.reverse()
        @content.append(add_items)

    init_message: (item) ->
        item.find('.message-control .hide').click((ev) =>
            li = $(ev.currentTarget).closest('li')
            message_id = li.attr('id').substring(11);
            @comm.sent(
                'hide_message',
                message_id: message_id,
                visitor_id: JS_DATA.visitor_id
            )
            li.addClass('hide')
        )


class Response
    columns: ->
        first_col_height = $('body > .page-wrapper > .content > .column:eq(0)').height()
        media_height = $('.media').height()
        $('.chat .content-wrapper').height(first_col_height - media_height - 69)


response = new Response()


$(document).ready ->
        #=======================================================================
        new Chat()
        #=======================================================================
        show_size = () ->
            width = $(window).width()
            test = $('#test')
            if not test.length
                test = $('<div>').attr('id', 'test')
                $('body').prepend(test)
            test.text width

        set_text_size = ->
            $('.info .cover-wrapper .summary').css({
                fontSize: ($('.info .cover-wrapper .cover').width() / 200) + 'rem'
            })

        set_text_size()
        # show_size()

        $(window).resize ->
            # show_size($()
            set_text_size()
            response.columns()

        if JS_DATA.is_mobile
            $('footer').insertAfter(".info")

        $('.chat > .chat-hidden').click(->
            $('.chat').toggleClass('show-hidden')
        )


$(window).load ->
    response.columns()
