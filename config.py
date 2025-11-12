#!/usr/bin/env python3

config = {

  # Set 'app_path' to a custom value to change the default path that will be used to route the index page of the app.
  # For example, if the value is "/webs3", the default url of the web app will be something like 
  # "https://localhost:8003/webs3", rather than "https://localhost:8003/".

  'app_path'  : '/webs3',

  'aws_credentials_file' : '/user/aws/credentials',

  # AWS Credentials File (ini format)
  # -----
  # [default]
  # aws_access_key_id = ACCESSKEY
  # aws_secret_access_key = SECRETACCESSKEY
  # -----

  # Set 'secret_key' to set an app.secret_key for Flask.

  'secret_key'  : 'SECRETKEYFORFLASK',
  
  # Set 'parse_html' to True to enable webs3 to parse & render html files. Please note that scripts and styles that are
  # included within the html code will be rendered and processed by the browser as well. Make sure the html files are
  # safe to be processed if you enable the 'parse_html' option.

  'parse_html'  : False,

  # Set 'parse_markdown' to True to enable webs3 to parse & render markdown files with a default Github flavored style.
  # If enabled, the app will use the marko library: https://marko-py.readthedocs.io/en/latest/ to parse '.md' files.

  'parse_markdown'  : True,

  # Set 'parse_rst' to True to enable webs3 to parse & render rst (reStructuredText) files with a default Github flavored style.
  # If enabled, the app will use the docutils library: https://docutils.sourceforge.io/rst.html to parse '.rst' files.

  'parse_rst'  : True,

}
