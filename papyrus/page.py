from .basepage import BasePage

class Page(BasePage):
    def __init__(self, input_path):
        super().__init__(input_path)

    def __str__(self):
        return "Page at {}: {}".format(self.url, self.title)

    def build(self, pandoc, config):
        super().build(pandoc, config)

        if self.layout != 'jinja':
            if not self.is_current():
                print("Building page: ", self)
                self.generate_html(pandoc)

    def __render(self, jinja_env, site_meta, page_meta):
        if self.layout == 'jinja':
            template = jinja_env.from_string(self.content_text)
            return template.render(meta=self.meta, page=page_meta, site=site_meta)
        else:
            if not self.is_current():
                template = jinja_env.get_template("{}.html".format(self.layout))
                return template.render(content=self.content_html, page=page_meta, meta=self.meta, site=site_meta)
            else:
                return None

    def write(self, jinja_env, site_meta):
        template_out = self.__render(jinja_env, site_meta, self.get_page_metadata())
        if template_out:
            print("Writing page:", self)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(template_out)
            return True
        return False
