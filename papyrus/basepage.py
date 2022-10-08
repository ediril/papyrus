import frontmatter
import pathlib
import datetime
import os
import re

class BasePage():
    def __init__(self, input_path):
        self.input_path = input_path
        self.content_text = None
        self.content_html = None
        self.excerpt_text = None
        self.excerpt_html = None
        self.output_path = None
        self.layout = None
        self.url = None
        self.props = None
        self.title = ""
        self.date = None
        self.tags = []

        self.__update()

    def __update(self):
        with self.input_path.open() as infile:
            content = infile.read()
        # parse and remove front matter
        front_meta, content = frontmatter.parse(content)
        # parse and remove back matter
        back_meta, content = self.parse_backmatter(content)

        self.meta = front_meta | back_meta
        self.title, self.content = self.extract_title(content)
        if not self.title:
            self.title = self.meta['title'] if 'title' in self.meta else None
        self.layout = self.meta['layout'] if 'layout' in self.meta else 'post'
        self.date = self.get_date(self.meta, self.input_path)
        self.url = self.get_url(self.meta)
        self.props = self.meta['props'].split(" ") if "props" in self.meta else []
        self.tags = self.meta['tags'].split(" ") if ('tags' in self.meta and self.meta['tags']) else []

    def build(self, pandoc, config):
        self.__update()

        self.excerpt_text, self.content_text = \
            self.get_excerpt_content(self.content, config['EXCERPT_SEPARATOR'])
        self.output_path = self.get_output_path(config['DIR_PUBLISH'])

    @staticmethod
    def parse_backmatter(content):
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
        first_line = content[0:ii_first_newline].strip()
        if first_line.startswith("#"):
            content = content[ii_first_newline:].strip()
            return first_line.replace("#", "").strip(), content

        return None, content

    def is_draft(self):
        if 'draft' in self.props:
            return True
        return False

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
            return None, splittext[0].strip()

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

    def render(self, jinja_env, site_meta, page_meta):
        raise NotImplementedError()

    def write(self, jinja_env, site_meta):
        template_out = self.render(jinja_env, site_meta, self.get_page_metadata())
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(template_out)

    def get_page_metadata(self):
        page = {
            'title': self.title,
            'excerpt': (hasattr(self, 'excerpt_html') and self.excerpt_html) or '',
            'url': self.url
        }
        return page
