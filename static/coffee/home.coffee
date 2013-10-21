
$(document).ready ->
        window.user_info = new window.UserInfo(
            container: $('.block.user_info .content-wrapper'),
        )

        comm = new window.Comm()

        new window.Chat(
            comm: comm,
            container: $('.block.chat .content-wrapper'),
            input_box: $('.block.chat .input-box'),
            code: 'main',
        )

        (new window.Mod()).after_install()

(new Response()).main()
