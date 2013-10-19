
class window.Chat
    constructor: (data) ->
        @comm = data.comm
        @code = data.code
        @container = data.container
        @input_box = data.input_box
        @content    = $('<ul>').addClass('content')
        @chat_input = @input_box.find('input')

        @comm.onmessage 'chat', @onmessage.bind this

        @add_messages(JS_DATA.last_messages)
        @init_sent()

        @container.append($('<div>').addClass('up_beam'))
        @container.append(@content)

        $('body .chat .sent').click =>
            @sent 'chat_message', msg: @chat_input.val()
            @chat_input.val('').focus()

        # if ! JS_DATA.is_mobile
        #     setTimeout(
        #         =>
        #             @chat_input.focus()
        #             $.injectCSS
        #                 '.chat .input-box input':
        #                     'animation': 'ma_ab1 .5s',
        #                     '-webkit-animation': 'ma_ab1 .5s'
        #         400
        #     )

        @show_users_count JS_DATA.users_count

    sent: (action, data) ->
        data.code = @code
        @comm.sent action, data

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
                    @sent 'chat_message', msg: target.val()
                    target.val ''

    show_users_count: (count) ->
            $('.chat .chat-info dd').text(count)

    onmessage: (data) ->
        if data.add_message isnt undefined
            @add_messages([data.add_message])
        else if data.users_count isnt undefined
            @show_users_count data.users_count
        else if data.check_user isnt undefined
            @sent 'check_user_live', user_id: JS_DATA.stream_user_id

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
            @sent(
                'hide_message',
                message_id: message_id,
                visitor_id: JS_DATA.visitor_id
            )
            li.addClass('hide')
        )
