# Starter configuration file copied on init

### local directory setup
DIR_PUBLISH   = "_pub"
DIR_PAGES     = "pages"
DIR_FILES     = "files"
POST_STORE    = "post_store.db"

### public-facing site metadata
SITE = {
    'title':        "Papyrus",
    'description':  "A simple static site generator",
    'site_name':    "example.com",
    'absolute_url': "https://example.com",
    'base_url':     "",
    'template':     "default",
    'static_folder': "static",
    'twitter':      "@example",
    'github':       "https://github.com/example",
    'recent_posts': 5,
    'maincss':      "/css/main.css",
    'rssfeed':      "feed.xml"
}

PANDOC_ARGS = "markdown+backtick_code_blocks+inline_code_attributes"
EXCERPT_SEPARATOR = "<!--excerpt-->"

### development server
SERVER_PORT = 9988

### S3 deployment
AWS_PROFILE = "aws_profile_name"
S3_BUCKET = "s3_bucket_name"
S3_USE_GZIP = True
S3_GZIP_COMPRESSION = 9
S3_GZIP_FILES = [
    "*.html",
    "*.css",
    "*.js",
    "*.txt"
]
S3_GZIP_MINSIZE = 1024

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
