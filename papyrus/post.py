
from .basepage import BasePage

class Post(BasePage):
    def __init__(self, input_path):
        super().__init__(input_path)

        self.wordcount = 0

    def __str__(self):
        if self.date:
            return "Post on {}: {}".format(self.date.isoformat(), self.title)
        else:
            return "Post: {}".format(self.title)

    def build(self, pandoc, config):
        super().build(pandoc, config)

        if not self.title:
            self.title = self.input_path.name.replace(".md", "")

        self.wordcount = pandoc.countwords(self.input_path)

        if not self.is_current():
            print("Building post: ", self)
            self.generate_html(pandoc)

    def __render(self, jinja_env, site_meta, page_meta):
        template = jinja_env.get_template("{}.html".format(self.layout))
        return template.render(content=self.content_html, post=self, page=page_meta, site=site_meta)

    def write(self, jinja_env, site_meta):
        if not self.is_current():
            print("Writing post:", self)
            template_out = self.__render(jinja_env, site_meta, self.get_page_metadata())
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(template_out)
            return True
        return False
