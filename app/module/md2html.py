import re
import markdown2


class MD2Html:
    def __init__(self):
        self.md = markdown2.Markdown()

    def _set_tag_attr(self, a):
        tag = a.group(1)
        attr = 'class' if a.group(2) == '.' else 'id'
        value = a.group(3)
        return '<%s %s="%s">' % (tag, attr, value)

    def convert(self, text):
        p1 = re.compile(r'^\s*(<--.*|-->)', re.MULTILINE)
        p2 = re.compile(r'<--([\d\w_-]*)')
        p3 = re.compile('<(.*?)>\{([.#])(.*?)\}')

        text = p1.split(text)

        if len(text) > 1:
            for i in range(len(text)):
                if i % 2:
                    r = p2.search(text[i])
                    if r:
                        text[i] = (
                            '<div%s>' % (
                                ' class="%s"' % r.group(1)
                                if r.group(1) else
                                ''
                            )
                        )
                    else:
                        text[i] = '</div>'
                else:
                    text[i] = self.md.convert(text[i])
                    text[i] = p3.sub(self._set_tag_attr, text[i])

        return ''.join(text)

    def markdown_convert(self, text):
        p = re.compile('^<->', re.MULTILINE)
        return ''.join([self.convert(i) for i in p.split(text)])
