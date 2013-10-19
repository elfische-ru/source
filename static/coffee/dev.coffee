
class window.DevInstance
    get_block: ->
        dev_block = $('#dev_block')
        if not dev_block.length
            dev_block = $('<div>').attr('id', 'dev_block')
            $('body').prepend(dev_block)
        return dev_block

    show: (text) ->
        block = @get_block()
        block.html(text)


window.Dev = new DevInstance()
