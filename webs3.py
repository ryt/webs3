#!/usr/bin/env python3

# This app uses boto3, Flask, and Gunicorn.

# Related Notes:
# S3 Browser React+Vite Web App by AWS: 
# - https://github.com/aws-samples/sample-amplify-storage-browser

v = '0.0.1'

"""
Copyright (C) 2025 Ray Mentose.
Latest version of the project on Github at: https://github.com/ryt/webs3
"""

import os
import csv
import html
import json
import boto3
import config
import itertools

from flask import Flask
from urllib.parse import quote
from flask import render_template
from flask import send_file, abort
from flask import request, session, redirect

from configparser import ConfigParser
from botocore.exceptions import ClientError

app = Flask(__name__)

# -- start: parse config parameters from config.py and set values

# default config values

limitpath = ''
app_path  = '/webs3'
secret_key = ''
aws_credentials_file = ''

parse_html      = False
parse_markdown  = False
parse_rst       = False

# read & modify config values

if 'limitpath' in config.config:
  limitpath = config.config['limitpath'].rstrip('/') + '/'

if 'app_path' in config.config:
  app_path = config.config['app_path']

if 'aws_credentials_file' in config.config:
  aws_credentials_file = config.config['aws_credentials_file']

if 'parse_html' in config.config:
  parse_html = config.config['parse_html']

if 'parse_markdown' in config.config:
  parse_markdown = config.config['parse_markdown']

if 'parse_rst' in config.config:
  parse_rst = config.config['parse_rst']

if 'secret_key' in config.config:
  secret_key = config.config['secret_key']

# -- end: parse config parameters

if secret_key:
  app.secret_key = secret_key

# parse aws_credentials_file (ini format) & load keys
aws_connected = False
aws_access = ''

if aws_credentials_file:
  awscred = ConfigParser()
  awscred.read(aws_credentials_file)
  if awscred.has_section('default'):
    aws_access = awscred.get('default', 'aws_access_key_id')
    aws_secret = awscred.get('default', 'aws_secret_access_key')
    s3_client = boto3.client(
      's3',
      aws_access_key_id=aws_access,
      aws_secret_access_key=aws_secret,
      region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    aws_connected = True

# markdown options
if parse_markdown == True:
  from marko.ext.gfm import gfm

# rst options
if parse_rst == True:
  from docutils import core


def get_query(param):
  """Get query string param (if exists & has value) or empty string"""
  try:
    return request.args.get(param) if request.args.get(param) else ''
  except:
    return ''

def remove_from_start(sub, string):
  """Remove sub from beginning of string if string starts with sub"""
  if string.startswith(sub):
    return string[len(sub):].lstrip()
  else:
    return string

def remove_limitpath(path):
  """Remove limitpath from beginning of path if limitpath has value"""
  global limitpath
  return remove_from_start(limitpath, path) if limitpath else path

def add_limitpath(path):
  """Add limitpath to beginning of path if limitpath has value"""
  global limitpath
  return f'{limitpath}{path}' if limitpath else path

def sanitize_path(path):
  """Sanitize path for urls: 1. apply limitpath mods, 2. escape &'s and spaces"""
  return quote(remove_limitpath(path), safe='/')

sp = sanitize_path

def parse_filter(qfilter):
  """Parse a filter (query) string and convert it into dictionary with keys, values, & attributes"""
  filter_dicts = []
  filter_instances = qfilter.split(',')
  for f in filter_instances:
    filter_parts = f.split(':')
    filter_key = filter_parts[0]
    filter_val = filter_parts[1]
    filter_col_num = int(''.join(filter(str.isdigit, filter_key)))
    filter_dicts.append({
      'key'     : filter_key,
      'col_num' : filter_col_num,
      'val'     : filter_val
    })

  return filter_dicts

def filter_compare(csv_value, search_value):
  """Compares csv_value & search_value and determines if the filters match or not"""

  # quoted strings == exact match

  if (search_value.startswith('"') and search_value.endswith('"')) or (search_value.startswith("'") and search_value.endswith("'")):
    if search_value.strip('\'"') == csv_value:
      return True
    else:
      return False

  # non-quoted strings = search

  elif search_value in csv_value:
    return True

  return False

def html_return_error(text):
  return f'<div class="error">{text}</div>'

def html_render_csv(path):

  render   = ''
  path_mod = remove_limitpath(path)

  try:

    with open(path, 'r') as file:

      getfilter = get_query('filter')
      getsort = get_query('sort')
      html_table = ''

      content = file.read()

      if getfilter:
        filter_insts = parse_filter(getfilter)
        filter_ihtml = [f"<b>{f['key']}</b> = <b>{f['val']}</b>" for f in filter_insts]
        html_table = f'<div class="top-filter hide-on-hide">Applying filter: {", ".join(filter_ihtml)}. Filtered rows: ##__filtered_rows__##.</div>'


      html_table += '<table class="csv-table">\n'
      # added {skiinitialspace=True} to fix issue with commas inside quoted cells
      csv_reader = csv.reader(content.splitlines(), skipinitialspace=True)
      headers = next(csv_reader)

      html_table += '<tr>'
      for header in headers:
        header = html.escape(header)
        html_table += f'<th>{header}</th>'
      html_table += '</tr>\n'

      filtered_rows = 0

      if getsort:
        if getsort == 'za':
          csv_reader = reversed(list(csv_reader))

      for row in csv_reader:
        display_row = True

        if getfilter:
          display_row = False
          fi = filter_insts
          table_row = '<tr>'

          if len(fi) > 1: # multiple filters (AND search)
            found_count = 0

            for fx in fi:
              if 0 <= fx['col_num']-1 < len(row) and filter_compare(row[fx['col_num']-1], fx['val']):
                found_count += 1 # add 1 for each found filter

            if found_count == len(fi):
              display_row = True

          else: # single filter
            if 0 <= fi[0]['col_num']-1 < len(row) and filter_compare(row[fi[0]['col_num']-1], fi[0]['val']):
              display_row = True


          for cell in row:
            cell = html.escape(cell)
            table_row += f'<td>{cell}</td>'

          table_row += '</tr>\n'

        else:
          table_row = '<tr>'
          for cell in row:
            cell = html.escape(cell)
            table_row += f'<td>{cell}</td>'
          table_row += '</tr>\n'

        if display_row:
          filtered_rows += 1
          html_table += table_row
      

      html_table += '</table>'

      render = html_table.replace('##__filtered_rows__##', str(filtered_rows))

  except FileNotFoundError:
    render = html_return_error(f"The file '{path_mod}' does not exist.")

  except:
    render = html_return_error(f"The file '{path_mod}' could not be parsed.")

  return render


def plain_render_file(path):

  render   = ''
  path_mod = remove_limitpath(path)

  try:
    with open(path, 'r') as file:
      try:
        render = file.read()
      except:
        render = f"The file '{path_mod}' is not in text format."

  except FileNotFoundError:
    render = f"The file '{path_mod}' does not exist."

  except IOError:
    render = f"Error reading the file '{path_mod}'."

  return render


def browser_load_file(path, redirect_send=False):

  parts  = path.strip('/').split('/', 1)
  bucket = parts[0]
  key    = parts[1]

  try:
    url = s3_client.generate_presigned_url(
      'get_object',
      Params = { 'Bucket': bucket, 'Key': key },
      ExpiresIn = 300 # 5 minutes
    )
    if redirect_send == True:
      return redirect(url)
    else:
      return url

  except Exception as e:
    return { 'error': str(e) }, 500

def noncsv_render_file(path, ftype):

  render   = ''
  path_mod = remove_limitpath(path)

  try:
    with open(path, 'r') as file:
      try:
        if ftype == 'markdown':
          render = f'<article class="markdown-body">{gfm(file.read())}</article>'
        elif ftype == 'rst':
          render = f'<article class="markdown-body">{core.publish_parts(source=file.read(), writer_name="html")["html_body"]}</article>'
        elif ftype == 'html':
          render = file.read()
        else:
          render = f"The file '{path_mod}' is not in supported format."
      except:
        render = f"The file '{path_mod}' is not in a supported format."

  except FileNotFoundError:
    render = f"The file '{path_mod}' does not exist."

  except IOError:
    render = f"Error reading the file '{path_mod}'."

  return render

def list_buckets():
  try:
    # List all buckets
    response = s3_client.list_buckets()
    
    buckets = []
    for bucket in response['Buckets']:
      buckets.append({
        'name': bucket['Name'],
        'creation_date': bucket['CreationDate'].isoformat()
      })
    
    return {
      'total_buckets': len(buckets),
      'buckets': buckets
    }
    # json.dumps({}, indent=4)
    
  except ClientError as e:
    return {'error': str(e)}, 500

def list_bucket(bucket_name):
  if not aws_connected:
    return { 'error': 'AWS connection failed.' }, 500

  try:
    page_size   = int(request.args.get('page_size', 100))
    direction   = request.args.get('direction', 'next')  # "next" or "prev"
    page_number = int(request.args.get('page', 1))
    session_key = f"s3_pagination_{bucket_name}"

    # initialize pagination session state
    if session_key not in session:
      session[session_key] = {
        'start_keys' : [None]
      }

    state  = session[session_key]
    params = { 'Bucket': bucket_name, 'MaxKeys': page_size }

    # handle navigation direction
    if page_number > 1:
      start_after = state['start_keys'][page_number - 1]
      if start_after:
        params['StartAfter'] = start_after

    # fetch the current page
    response = s3_client.list_objects_v2(**params)
    objects = [
      {
        'key'  : obj['Key'],
        'size' : obj['Size'],
        'last_modified': obj['LastModified'].isoformat()
      }
      for obj in response.get('Contents', [])
    ]

    # handle continuation tokens for next page
    next_token   = response.get('NextContinuationToken') # used only to determine if there's more items
    is_truncated = response.get('IsTruncated', False)

    # store state for this session
    if next_token and len(state['start_keys']) <= page_number:
      last_key = objects[-1]['key'] if objects else None
      state['start_keys'].append(last_key)
      session[session_key] = state

    return {
      'bucket'    : bucket_name,
      'page'      : page_number,
      'direction' : direction,
      'page_size' : page_size,
      'objects'   : objects,
      'total_objects' : len(objects),
      'has_next'  : bool(next_token),
      'has_prev'  : page_number > 1
    }

  except ClientError as e:
    code = e.response['Error']['Code']
    if code == 'NoSuchBucket':
      return {'error': 'Bucket does not exist'}, 404
    elif code == 'AccessDenied':
      return {'error': 'Access denied to bucket'}, 403
    else:
      return {'error': str(e)}, 500


@app.route(app_path, methods=['GET'])

def index(subpath=None):

  # if limitpath is set in config, the directory listing view for the client/browser will be limited to that path as the absolute parent
  # if app_path is set in config, that path will be used to route index page of the app

  global limitpath, app_path

  # limitpath = '/usr/local/share/' # for testing

  getf        = get_query('f')
  getshow     = get_query('show')
  getsort     = get_query('sort')
  getpage     = get_query('page')
  getfilter   = get_query('filter')
  getdark     = get_query('dark')
  getsession  = get_query('session')
  getf_html   = remove_limitpath(getf)  # limitpath mods for client/browser side view
  getf        = add_limitpath(getf)     # limitpath mods for internal processing

  getpage_m   = 1 if not getpage else int(getpage)

  view   = { 
    'app_path'  : app_path,
    'getsort'   : getsort,
    'getfilter' : getfilter,
    'getdark'   : getdark,
    'dirlist'   : False,
  }
  listfs = []
  total = { 'text': '', 'count': 0 }

  nav_prev = ''
  nav_next = ''

  if getf == '/':
    view['dirlist'] = True
    files = list_buckets()
    total = { 'text': 'Total Buckets', 'count': files['total_buckets'] }
    parpt = getf.rstrip('/')
    if files['buckets']:
      for f in files['buckets']:
        name = f['name']
        listfs.append({ 
          'name' : f'{name}/', 
          'path' : sp(f'{parpt}/{name}/')
        })

  elif getf.startswith('/') and getf.endswith('/') and getf.count('/') <= 2: 
  # starts (and ends) with / and has less than or equal to 2 / (e.g. bucket)
    view['dirlist'] = True
    files = list_bucket(getf.strip('/'))
    total = { 'text': 'Total Objects', 'count': files['total_objects'] }
    parpt = getf.rstrip('/')
    if files['objects']:
      for f in files['objects']:
        name = f['key']
        if name.endswith('/'): # isdir / isbucket
          listfs.append({ 
            'name' : f'{name}', 
            'path' : sp(f'{parpt}/{name}')
          })
        else:
          listfs.append({ 
            'name' : name, 
            'path' : sp(f'{parpt}/{name}')
          })
    nav_prev = f'?f={getf}&page={getpage_m-1}' if files['has_prev'] else ''
    nav_next = f'?f={getf}&page={getpage_m+1}' if files['has_next'] else ''


  else:
    # session page
    if getsession and getsession in ('show','clear'):
      if getsession == 'clear':
        session.clear()
      view['session_data'] = json.dumps(dict(session), indent=4)

    # additional non-csv rendering options

    # inline
    elif getshow == 'inline':
      view['noncsv'] = True
      view['show_inline'] = 'Displaying inline.'
      view['inline_url'] = browser_load_file(getf, False)

    # load
    elif getshow == 'load':
      return browser_load_file(getf, True)

    # raw
    elif getshow == 'raw':
      return plain_render_file(getf), 200, { 'Content-Type': 'text/plain' }

    else:
      # --- start: default webcsv noncsv options (markdown, rst, html) --- #
      # markdown
      if parse_markdown == True and getf.endswith('.md'):
        view['noncsv'] = True
        view['noncsv_markdown'] = noncsv_render_file(getf, 'markdown')
        with open('assets/github-markdown.css', 'r') as github_markdown:
          view['markdown_css'] = github_markdown.read()
          if getdark != 'false':
            with open('assets/github-markdown-dark.css', 'r') as github_markdown_dark:
              view['markdown_css'] = ' '.join((github_markdown_dark.read(), view['markdown_css']))
      # rst
      elif parse_rst == True and getf.endswith('.rst'):
        view['noncsv'] = True
        view['noncsv_rst'] = noncsv_render_file(getf, 'rst')
        with open('assets/github-markdown.css', 'r') as github_markdown:
          view['rst_css'] = github_markdown.read()
          if getdark != 'false':
            with open('assets/github-markdown-dark.css', 'r') as github_markdown_dark:
              view['rst_css'] = ' '.join((github_markdown_dark.read(), view['rst_css']))
      # html
      elif parse_html == True and (getf.endswith('.htm') or getf.endswith('.html')):
        view['noncsv'] = True
        view['noncsv_html'] = noncsv_render_file(getf, 'html')

      # --- end: default webcsv noncsv options --- #

      else:
        view['noncsv'] = True

  # csv
  if getf.endswith('.csv') and getshow != 'plain':
    view['csvshow'] = html_render_csv(getf)
    view['noncsv']  = False

  address   = []
  addrbuild = ''
  if getf_html: 
    pathf = getf_html.strip('/').split('/')
    pathf_len = len(pathf)
    i = 0
    for path in pathf:
      endslash = '/'
      if not getf_html.endswith('/') and i == pathf_len-1: # ignore slash after file ext & extra slash
        endslash = ''
      addrbuild += f'/{path}'
      address.append({ 
        'name'      : f'{path}', 
        'path'      : sp(f'{addrbuild}' + endslash),
        'separator' : '/'
      })
      i += 1

  view['aws_access']      = aws_access
  view['listfs']          = listfs
  view['total']           = total
  view['address']         = address
  view['getf_html']       = getf_html
  view['getf_html_sp']    = sp(getf_html)
  view['getshow_query']   = f'&show={getshow}' if getshow else ''
  view['getsort_query']   = f'&sort={getsort}' if getsort else ''
  view['getfilter_query'] = f'&filter={getfilter}' if getfilter else ''
  view['show_header']     = False if get_query('hide') == 'true' else True

  view['nav_prev']        = nav_prev
  view['nav_next']        = nav_next


  return render_template('template.html', view=view)


if __name__ == '__main__':
    app.run(debug=True)

