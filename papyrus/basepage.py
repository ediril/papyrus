import frontmatter
import pathlib
import datetime
import os

NOT_NOTE = ["link", "image", "tweet", "music", "pdf"]

class BasePage:

    def __init__(self, input_path):
        self.input_path = input_path
        self.meta = None
        self.date = None
        self.title = None
        self.props = None
        self.layout = None
        self.url = None
        self.tags = None
        self.output_path = None
        self.content_text = None
        self.content_html = None
        self.excerpt_text = None
        self.excerpt_html = None

    def build(self, pandoc, config):
        with self.input_path.open() as infile:
            content = infile.read()
        self.meta, content = frontmatter.parse(content)

        self.date = self.get_date(self.meta, self.input_path)
        self.props = self.meta['props'].split(" ") if "props" in self.meta else []
        self.title, content = self.extract_title(content)
        self.layout = self.meta['layout'] if 'layout' in self.meta else 'post'
        self.url = self.get_url(self.meta, self.input_path)
        self.tags = self.meta['tags'].split(" ") if ('tags' in self.meta and self.meta['tags']) else []

        self.output_path = self.get_output_path(config['DIR_PUBLISH'])
        self.excerpt_text, self.content_text = \
            self.get_excerpt_content(content, config['EXCERPT_SEPARATOR'])

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

    def is_tweet(self):
        if 'tweet' in self.props:
            return True
        return False

    def is_image(self):
        if 'image' in self.props:
            return True
        return False

    def is_link(self):
        if 'link' in self.props:
            return True
        return False

    def is_x(self, prop):
        if prop in self.props:
            return True
        return False

    def is_note(self):
        return all(p not in self.props for p in NOT_NOTE)

    def is_public(self):
        if not self.props:
            return True

        if "public" in self.props:
            return True

        if all(p not in self.props for p in ["private", "draft"]):
            return True

        return False

    @staticmethod
    def get_date(meta, input_path):
        pagedate = None
        try:
            pagedate = datetime.date.fromisoformat(str(meta['date']))
        except:
            pass
        if pagedate is None:
            try:
                pagedate = datetime.date.fromisoformat(str(input_path.stem[:10]))
            except:
                pass
        if pagedate is None:
            created_ts = int(os.stat(input_path.as_posix()).st_birthtime)
            pagedate = datetime.date.fromtimestamp(created_ts)
        return pagedate

    @staticmethod
    def get_url(meta, input_path):
        if 'path' in meta:
            if meta['path'] == '/':
                return "/index.html"
            else:
                return meta['path']
        else:
            return input_path.with_suffix('').name

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
            self.excerpt_html = self.excerpt_html.replace('<p>', '').replace('</p>', '')

    def is_current(self):
        if self.output_path is None or not self.output_path.exists():
            return False
        if self.input_path.stat().st_mtime >= self.output_path.stat().st_mtime:
            return False
        else:
            return True

    def write(self, jinja_env, site_meta):
        raise NotImplementedError("Method not implemented in base class")

    def get_page_metadata(self):
        page = {
            'title': self.title,
            'excerpt': (hasattr(self, 'excerpt_html') and self.excerpt_html) or '',
            'url': self.url
        }
        return page
