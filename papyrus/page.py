from .basepage import BasePage

class Page(BasePage):
    def __init__(self, input_path, meta, content):
        print("Creating Page from file:", input_path)
        super().__init__(input_path, meta, content)

    def __str__(self):
        return "Page at {}: {}".format(self.url, self.title)

    def build(self, pandoc, config):
        super().build(pandoc, config)

        self.title = self.meta['title'] if 'title' in self.meta else ""

        if not self.is_current():
            if self.layout != 'jinja':
                self.generate_html(pandoc)

    def render(self, jinja_env, site_meta, page_meta):
        print("Writing page:", self)

        if self.layout == 'jinja':
            template = jinja_env.from_string(self.content_text)
            return template.render(meta=self.meta, page=page_meta, site=site_meta)

        else:
            template = jinja_env.get_template("{}.html".format(self.layout))
            return template.render(content=self.content_html, page=page_meta, meta=self.meta, site=site_meta)
