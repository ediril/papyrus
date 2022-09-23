# Starter configuration file copied on init

### local directory setup
DIR_PUBLISH   = "_pub"
DIR_POSTS     = "posts"
DIR_PAGES     = "pages"
DIR_DRAFTS    = "drafts"
DIR_STATIC    = "static"
DIR_TEMPLATES = "templates"
POST_STORE    = "post_store.db"

### public-facing site metadata
SITE = {
    'title':        "Papyrus",
    'description':  "A simple static site generator",
    'site_name':    "example.com",
    'author':       ("author", "/about/"),
    'author_name':  "Namely McNameworthy",
    'absolute_url': "https://example.com",
    'base_url':     "",
    'twitter':      "@example",
    'github':       "https://github.com/example",
    'links': [
        ("Home", "/"),
        ("About", "/about/"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Main_Page"),
        ("RSS Feed", "/feed.xml"),
    ],
    'recent_posts': 10,
    'maincss':      "/css/main.css",
    'rssfeed':      "feed.xml"
}

PANDOC_ARGS = "markdown+backtick_code_blocks+inline_code_attributes"
EXCERPT_SEPARATOR = "<!--excerpt-->"
TOPICS_URL_PREFACE = "topics"

### pagination
POSTS_PER_PAGE = 10

### development server
SERVER_PORT = 9988

### deployment

### files matching these patterns will never be updated or deleted from S3
IGNORE_ON_SERVER = [
    "legacy*",
    "contact.html",
]

### files matching these patterns will bever be uploaded to S3
EXCLUDE_FROM_UPLOAD = [
    "*.DS_Store",
    "*.upload",
]

# Default format for post urls: "/YYYY/MM/DD/slug/"
def FN_POST_URL(args):
    url = "/{}/{}/{}/{}/".format(
        args['meta']['date'].strftime("%Y"),
        args['meta']['date'].strftime("%m"),
        args['meta']['date'].strftime("%d"),
        args['input_path'].stem[11:]
    )
    return url


