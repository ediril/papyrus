import pathlib
import datetime
import os
import re

import frontmatter

class BasePage():
    def __init__(self, input_path):
        self.input_path = input_path
        self.output_path = None
        self.layout = None
        self.url = None
        self.props = None
        self.title = ""
        self.date = None
        self.wordcount = 0
        self.topics = []
        self.content_text = None
        self.content_html = None
        self.excerpt_text = None
        self.excerpt_html = None

    def build(self, pandoc, config):
        with self.input_path.open() as infile:
            self.content_text = infile.read()
        # parse and remove front matter
        front_meta, content = frontmatter.parse(self.content_text)
        # parse and remove back matter
        back_meta, content = self.parse_back_matter(content)
        meta = front_meta | back_meta
        self.title, content = self.extract_title(content)
        self.excerpt_text, self.content_text = \
            self.get_excerpt_content(content, config['EXCERPT_SEPARATOR'])
        self.layout = meta['layout'] if 'layout' in meta else 'post'
        self.date = self.get_date(meta, self.input_path)
        self.url = self.get_url(meta)
        self.props = meta['props'].split(" ") if "props" in meta else []
        self.topics = ('topics' in meta and meta['topics'].split(" ")) or []
        self.output_path = self.get_output_path(config['DIR_PUBLISH'])

        if not self.is_current():
            self.generate_html(pandoc)
        self.wordcount = pandoc.countwords(self.input_path)

    @staticmethod
    def parse_back_matter(content):
        back_meta = {}
        ii = []
        for mo in re.finditer(r"^---\s*$", content, re.MULTILINE):
            ii.append(mo.start())

        if (len(ii)) == 2 and len(content) == ii[1] + 3:
            back_matter = content[ii[0]:]
            back_meta, _ = frontmatter.parse(back_matter)
            content = content[:ii[0]].strip()

        return back_meta, content

    @staticmethod
    def extract_title(content):
        ii_first_newline = content.find("\n")
        first_line = content[0:ii_first_newline]
        content = content[ii_first_newline:].strip()
        return first_line.replace("#", "").strip(), content

    def is_public(self):
        if not self.props:
            return True

        if "public" in self.props:
            return True

        if all(p not in self.props for p in ["private", "draft"]):
            return True

        return False

    def get_date(self, meta, input_path):
        pagedate = None
        try:
            pagedate = datetime.date.fromisoformat(str(meta['date']))
        except:
            pass
        if pagedate is None:
            try:
                pagedate = datetime.date.fromisoformat(str(self.input_path.stem[:10]))
            except:
                pass
        if pagedate is None:
            created_ts = int(os.stat(input_path.as_posix()).st_birthtime)
            pagedate = datetime.date.fromtimestamp(created_ts)
        return pagedate

    def get_url(self, meta):
        if 'path' in meta:
            if meta['path'] == '/':
                return "index.html"
            else:
                return meta['path']
        else:
            return self.input_path.with_suffix('').name

    def get_output_path(self, site_path):
        path = self.url
        if path.startswith("/"):
            path = path[1:]
        if path.endswith("/"):
            path += "index.html"
        return site_path / pathlib.Path(path)

    @staticmethod
    def get_excerpt_content(full_text, excerpt_sep):
        splittext = full_text.split(excerpt_sep, maxsplit=1)

        if len(splittext) < 2:
            return "", splittext[0].strip()

        return splittext[0].strip(), splittext[0] + splittext[1].strip()

    def generate_html(self, pandoc):
        self.content_html = pandoc.markup(input=self.content_text)
        if self.excerpt_text is not None:
            self.excerpt_html = pandoc.markup(input=self.excerpt_text)

    def is_current(self):
        if self.output_path is None or not self.output_path.exists():
            return False
        if self.input_path.stat().st_mtime >= self.output_path.stat().st_mtime:
            return False
        else:
            return True

    def write(self, jinja_env, site_meta):
        if not self.is_current():
            print("Writing:", self)
            template = jinja_env.get_template("{}.html".format(self.layout))
            page = self.get_page_metadata()
            template_out = template.render(content=self.content_html, page=page, post=self, site=site_meta)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(template_out)

    def get_page_metadata(self):
        page = {
            'title': self.title,
            'excerpt': (hasattr(self, 'excerpt_html') and self.excerpt_html) or '',
            'url': self.url
        }
        return page
