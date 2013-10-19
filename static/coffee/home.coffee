
$(document).ready ->
        comm = new window.Comm()

        main_chat = new window.Chat(
            comm: comm,
            container: $('.block.chat .content-wrapper'),
            input_box: $('.block.chat .input-box'),
            code: 'main',
        )

        (new window.Mod()).after_install()

(new Response()).main()
