import os
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
        self.content_files = sorted(pathlib.Path('.').glob('**/*.md'), key=lambda p: str(p.name))
        self.posts = []
        self.pages = []
        self.tags = {}
        self.jinja_env = None
        self.site_path = pathlib.Path('.') / self.config['DIR_PUBLISH']
        self.post_store = shelve.open(self.config['POST_STORE'])
        if args.target == 'prod':
            self.config['SITE']['base_url'] = self.config['SITE']['absolute_url']
        self.pandoc = Pandoc(self.config)
        self.template_path = pathlib.Path(__file__).parent / 'templates' / self.config['SITE']['template']

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
        static_path = self.template_path / self.config['SITE']['static_folder']
        copy_tree(static_path.resolve(), self.config['DIR_PUBLISH'])

        pub_files_dir = self.site_path / 'static' / self.config['DIR_FILES']
        if not os.path.isdir(pub_files_dir.resolve()):
            os.mkdir(pub_files_dir.resolve())
        files_dir = pathlib.Path('.') / self.config['DIR_FILES']
        copy_tree(files_dir.resolve(), str(pub_files_dir.resolve()))

    def configure_jinja_env(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_path.resolve()),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

    def read_content(self):
        for content_file in self.content_files:
            if content_file.name.endswith(".page.md"):
                page = Page(content_file)
                if page.is_public():
                    page.build(self.pandoc, self.config)
                    self.pages.append(page)

            else:
                if content_file.name in self.post_store:
                    post = self.post_store[content_file.name]
                    print("Reading Post from store: ", post)
                else:
                    post = Post(content_file)

                if post.is_draft():
                    print("Skipping draft post: ", post)

                elif post.is_public():
                    if not post.is_current():
                        post.build(self.pandoc, self.config)
                        self.post_store[post.input_path.name] = post
                    self.posts.append(post)

        self.posts = sorted(self.posts, key=attrgetter('date'), reverse=True)
        self.config['SITE']['posts'] = self.posts
        print("Read {} public posts".format(str(len(self.posts))))
        print("Read {} pages".format(str(len(self.pages))))

    def build_tags(self):
        for post in self.posts:
            for tag in post.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(post)
        self.config['SITE']['tags'] = self.tags

    def write_posts(self):
        post_cnt = 0
        for post in self.posts:
            if not post.is_current():
                post.write(self.jinja_env, self.config['SITE'])
                post_cnt += 1

        if post_cnt == 0:
            print("Public posts are up-to-date")
        else:
            print(f"Wrote {post_cnt} public post{'s' if post_cnt != 1 else ''}")

    def write_pages(self):
        for page in self.pages:
            page.write(self.jinja_env, self.config['SITE'])

        print(f"Wrote {len(self.pages)} public page{'s' if len(self.pages) != 1 else ''}")

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

    def write_rss_feed(self):
        print("Writing RSS feed...")
        # self.config['SITE']['timestamp'] = utils.format_datetime(datetime.datetime.utcnow())
        self.config['SITE']['timestamp'] = self.posts[len(self.posts)-1].date
        template = self.jinja_env.get_template("feed.xml")
        template_out = template.render(site=self.config['SITE'], page={})
        output_path = self.site_path / self.config['SITE']['rssfeed']
        output_path.write_text(template_out)

