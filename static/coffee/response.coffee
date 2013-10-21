
class window.Response
    main: ->
        $(document).ready ->
            chat = $('.block.chat')
            chat_wrapper = chat.find('> .content-wrapper')
            if chat_wrapper.height() == 0
                console.debug chat.height()
                chat_wrapper.height(340)
