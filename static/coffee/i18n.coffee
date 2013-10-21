
window.get_value_from_translations = (translations, msgid) ->
    ret = translations['catalog'][msgid]
    if (typeof(ret) == 'undefined' && translations['fallback'] != null)
        ret = get_value_from_translations(translations['fallback'], msgid)
    return ret

window.plural_index = (count, translations) ->
    eval 'var n = ' + count + '; var v = ' + translations['plural']
    return v

window.gettext = (msgid) ->
    value = get_value_from_translations(JS_DATA.js_translations, msgid)
    if (typeof(value) == 'undefined')
        return msgid
    else
        return if typeof(value) == 'string' then value else value[0]

window.ngettext = (singular, plural, count) ->
    value = get_value_from_translations(JS_DATA.js_translations, singular)
    if (typeof(value) == 'undefined')
        return if count == 1 then singular else plural
    else
        return value[plural_index(count, JS_DATA.js_translations)]

String.prototype.format = () ->
    args = arguments
    @replace(
        /{(\d+)}/g
        (match, number) ->
            if typeof args[number] != 'undefined' then args[number] else match
    )
