v0.3
- Change default config filename to `_site_config.py`
- Rename code folder to "papyrus"
- Move "template" folder out of "bootstrap" folder
  - Create a "default" template under "templates" and move them there
  - Copy "templates" folder to "DIR_TEMPLATES" 
- Move static folder to under template folder
  - Rename "DIR_STATIC" to "DIR_FILES" and copy it as is
- Add template selection to site config
  - Make "default" the default template
- Add a special layout called 'jinja2' that is like a page but md content becomes the page as is

v0.2
- "date" and "topics" are also optional
  - Get date from file creation if it is not specified
- Add support for back matter
- Rename topics as tags

v0.1
- Add the concept of "props"
  - Posts default to "private"
  - Generate HTML for only "public" posts
  - Replace "drafts" folder with "draft" prop
- Default layout is "post"
- First line is the title
- Post content includes the excerpt
- Eliminate POSTS_PER_PAGE
- Eliminate TOPICS_URL_PREFACE
- Disable topics (for now)

v0.0
- Fork from Stasis version v0.1.3