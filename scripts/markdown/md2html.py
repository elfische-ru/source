#!/usr/bin/env python3

import os
import re
import markdown
import lxml.html
import yaml
import template


class MD2Html:

    contents = []
    contents_items = []
    contents_id = 0

    def __init__(self,
                 md_files='.',
                 output_html_path='output.html',
                 header_file=None):

        self.md_files = md_files
        self.output_html_path = output_html_path
        self.header_file = header_file

        self.md = markdown.Markdown(output_format = 'html5')

    def _set_tag_attr(self, a):
        tag = a.group(1)
        attr = 'class' if a.group(2) == '.' else 'id'
        value = a.group(3)
        t = '<%s %s="%s">' % (tag, attr, value)
        return t

    def convert(self, text):
        html = self.md.convert(text)

        #===
        p = re.compile('<(.*?)>\{([.#])(.*?)\}')
        html = p.sub(self._set_tag_attr, html)

        #===
        p = re.compile('^<p>&lt;--(.*?)</p>$', re.MULTILINE)
        html = p.sub(r'<div class="\1">', html)

        p = re.compile('^<p>--&gt;</p>$', re.MULTILINE)
        html = p.sub('</div>', html)

        return html

    def get_text(self):
        header = None
        if os.path.isdir(self.md_files):
            files = [i for i in os.listdir(self.md_files) if i.endswith('.md')]
            files.sort()

            if self.header_file:
                for i, item in enumerate(files):
                    if item == self.header_file:
                        header = open(os.path.join(self.md_files, files.pop(i))).read()
                        break

            text = ''.join([open(os.path.join(self.md_files, i)).read() for i in files])
        else:
            text = open(self.md_files).read()

        return header, text

    def _nav_iter(self, a):
        self.contents_id += 1;
        value = {'item': a.groups(), 'id': self.contents_id, 'children': []}

        if not self.contents_items:
            self.contents_items.append(self.contents)
        if not self.contents_items[-1]:
            self.contents_items[-1].append(value)
        else:
            if self.contents_items[-1][-1]['item'][0] < a.group(1):
                self.contents_items[-1][-1]['children'].append(value)
                self.contents_items.append(self.contents_items[-1][-1]['children'])
            else:
                while self.contents_items[-1][-1]['item'][0] > a.group(1):
                    self.contents_items.pop()
                self.contents_items[-1].append(value)

        return '<h%s%s%s>%s</h%s>' % (
            a.group(1),
            a.group(2),
            ' id="n%s"' % self.contents_id,
            a.group(3),
            a.group(4),
        )

    def _nav_html(self, a):
        out = []
        for i in a:
            title = i['item'][2]
            children = self._nav_html(i['children']) if i['children'] else ''
            out.append('<li><a href="#n%s">%s</a>%s</li>' % (i['id'], title, children))
            level = i['item'][0]
        return '<ul class="level%s">%s</ul>' % (level, ''.join(out))

    def get_nav(self, content):
        p = re.compile('<h(\d+)(.*?)>(.*?)</h(\d+)>', re.MULTILINE)
        content = p.sub(self._nav_iter, content)
        self.contents_items = []
        return self._nav_html(self.contents), content

    def markdown_convert(self, text):
        p = re.compile('^<->', re.MULTILINE)
        return ''.join([self.convert(i) for i in p.split(text)])

    def get_out_html(self):
        header, content = self.get_text()
        header = self.markdown_convert(header) if header else ''
        content = self.markdown_convert(content)

        return {
            'header': header,
            'content': content,
        }

        # nav, content = self.get_nav(content)

        # return template.render(self.main_template_path, {
        #     'header': header,
        #     'nav': nav,
        #     'content': content,
        # })

    def save_html(self):
        out_html = self.get_out_html()

        out_html = re.sub('<hr>', '<hr/>', out_html)

        f = open(self.output_html_path, 'w')
        f.write(out_html)
        f.close()
