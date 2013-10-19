
class window.Mod
    set_text_size: ->
        $('.info .cover-wrapper .summary').css({
            fontSize: ($('.info .cover-wrapper .cover').width() / 200) + 'rem'
        })

    after_install: ->
        @set_text_size()

        $(window).resize =>
            @set_text_size()

        if JS_DATA.is_mobile
            $('footer').insertAfter(".info")

        $('.chat > .chat-hidden').click(->
            $('.chat').toggleClass('show-hidden')
        )
