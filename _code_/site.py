import pathlib
import shelve

from jinja2 import Environment, FileSystemLoader, select_autoescape
from distutils.dir_util import copy_tree
from operator import attrgetter

from .post import Post
from .page import Page
from .pandoc import Pandoc


class Site():
    def __init__(self, args, conf):
        self.config = conf
        self.post_inputs = sorted(pathlib.Path(self.config['DIR_POSTS']).glob('**/*.md'), key=lambda p: str(p.name))
        self.page_inputs = pathlib.Path(self.config['DIR_PAGES']).glob('**/*.md')
        self.posts = []
        self.pages = []
        self.tags = {}
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.config['DIR_TEMPLATES']),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        self.site_path = pathlib.Path('.') / self.config['DIR_PUBLISH']
        self.post_store = shelve.open(self.config['POST_STORE'])
        if args.target == 'prod':
            self.config['SITE']['base_url'] = self.config['SITE']['absolute_url']
        self.pandoc = Pandoc(self.config)

    def build(self):
        self.copystaticfiles()
        self.read_posts()
        # self.build_tags()
        self.write_posts()
        # self.write_tag_pages()
        self.read_pages()
        self.write_pages()
        # self.write_rss_feed()
        self.post_store.close()

    def copystaticfiles(self):
        copy_tree(self.config['DIR_STATIC'], self.config['DIR_PUBLISH'])

    def read_posts(self):
        for post_input in self.post_inputs:
            if post_input.name in self.post_store:
                post = self.post_store[post_input.name]
                print("Reading from post store: ", post)
            else:
                post = Post(post_input)
            if not post.is_current():
                post.build(self.pandoc, self.config)
                print("Building post: ", post)
            if post.is_public():
                self.posts.append(post)
        self.store_posts()
        self.posts = sorted(self.posts, key=attrgetter('date'), reverse=True)
        self.config['SITE']['posts'] = self.posts
        print("Read {} posts.".format(str(len(self.posts))))

    def read_pages(self):
        for page_input in self.page_inputs:
            page = Page(page_input)
            page.build(self.pandoc, self.config)
            self.pages.append(page)
        print("Read {} static pages.".format(str(len(self.pages))))

    def store_posts(self):
        for post in self.posts:
            self.post_store[post.input_path.name] = post

    def build_tags(self):
        for post in self.posts:
            for tag in post.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(post)
        self.config['SITE']['tags'] = self.tags

    def write_posts(self):
        print("Writing posts...")
        for post in self.posts:
            post.write(self.jinja_env, self.config['SITE'])

    def write_tag_pages(self):
        print("Writing tag pages...")
        template = self.jinja_env.get_template("tag.html")
        for tag in self.tags:
            print("  {}".format(tag))
            posts = self.tags[tag]
            posts.reverse()
            page = {
                'title': tag.title(),
                'url': f"/tags/{tag}/"
            }
            template_out = template.render(tag=tag, posts=posts, site=self.config['SITE'], page=page)
            tag_path = self.site_path / "tags" / tag
            tag_path.parent.mkdir(parents=True, exist_ok=True)
            tag_path.write_text(template_out)

    def write_pages(self):
        print("Writing static pages...")
        for page in self.pages:
            page.write(self.jinja_env, self.config['SITE'])

    def write_rss_feed(self):
        print("Writing RSS feed...")
        # self.config['SITE']['timestamp'] = utils.format_datetime(datetime.datetime.utcnow())
        self.config['SITE']['timestamp'] = self.posts[len(self.posts)-1].date
        template = self.jinja_env.get_template("feed.xml")
        template_out = template.render(site=self.config['SITE'], page={})
        output_path = self.site_path / self.config['SITE']['rssfeed']
        output_path.write_text(template_out)

