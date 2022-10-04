import frontmatter
import pathlib
import shelve
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape
from distutils.dir_util import copy_tree
from operator import attrgetter

from .post import Post
from .page import Page
from .pandoc import Pandoc


class Site():
    def __init__(self, args, conf):
        self.config = conf
        self.content_inputs = sorted(pathlib.Path('.').glob('**/*.md'), key=lambda p: str(p.name))
        self.posts = []
        self.pages = []
        self.tags = {}
        self.jinja_env = None
        self.site_path = pathlib.Path('.') / self.config['DIR_PUBLISH']
        self.post_store = shelve.open(self.config['POST_STORE'])
        if args.target == 'prod':
            self.config['SITE']['base_url'] = self.config['SITE']['absolute_url']
        self.pandoc = Pandoc(self.config)
        self.template_path = pathlib.Path('.') / self.config['DIR_TEMPLATES'] / self.config['SITE']['template']

    def build(self):
        self.copy_files()
        self.configure_jinja_env()
        self.read_content()
        # self.build_tags()
        self.write_posts()
        # self.write_tag_pages()
        self.write_pages()
        # self.write_rss_feed()
        self.post_store.close()

    def copy_files(self):
        copy_tree(self.config['DIR_FILES'], self.config['DIR_PUBLISH'])

        static_path = self.template_path / self.config['SITE']['static_folder']
        copy_tree(static_path.resolve(), self.config['DIR_PUBLISH'])


    def configure_jinja_env(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_path.resolve()),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

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

    def read_content(self):
        for content_input in self.content_inputs:
            with content_input.open() as infile:
                content_text = infile.read()

            # parse and remove front matter
            front_meta, content = frontmatter.parse(content_text)
            # parse and remove back matter
            back_meta, content = self.parse_back_matter(content)
            meta = front_meta | back_meta

            if 'layout' in meta:
                page = Page(content_input, meta, content)

                if meta['layout'] in ['page', 'jinja']:
                    page.build(self.pandoc, self.config)

                else:
                    raise ValueError("Unknown page layout")

                self.pages.append(page)

            else:
                if content_input.name in self.post_store:
                    post = self.post_store[content_input.name]
                    print("Reading from post store: ", post)
                else:
                    post = Post(content_input, meta, content)

                if not post.is_current():
                    post.build(self.pandoc, self.config)
                    print("Building post: ", post)

                if post.is_public():
                    self.posts.append(post)
                    self.post_store[post.input_path.name] = post

        self.posts = sorted(self.posts, key=attrgetter('date'), reverse=True)
        self.config['SITE']['posts'] = self.posts
        print("Read {} public posts.".format(str(len(self.posts))))
        print("Read {} pages.".format(str(len(self.pages))))

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
        print("Writing pages...")
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

