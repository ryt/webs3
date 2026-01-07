# webs3: Simple S3 Web Viewer

Simple python web app to browse S3 on a web browser. Derived from [webcsv](https://github.com/ryt/webcsv). 

This app uses [boto3](https://github.com/boto/boto3) for S3 connection, and [Flask](https://github.com/pallets/flask) & [Gunicorn](https://github.com/benoitc/gunicorn) (optionally with [ryt/runapp](https://github.com/ryt/runapp)) for deployment.

<!--
![](images/screen-shot-3.png)
![](images/screen-shot-2.png)
-->

## Test/Development Server

Run the app with the default Flask development server on port 5000.

```console
python3 webs3.py
```

> webs3 has been tested & deployed with the following versions of these libraries: 

- Python: **3.11.1**  
- Flask: **3.0.3**  
- boto3: **1.40.71**  
- Gunicorn: **23.0.0**   

> Your versions may or may not be compatible so double check your versions if you experience any issues.

## Deployment Instructions (with runapp)

> Note: the instructions below are for using the Gunicorn wrapper [runapp](https://github.com/ryt/runapp) to deploy the application. If you're using gunicorn by itself or are using a custom deployment process, you may skip these instructions.

Create & start a deployment, gunicorn (daemon/process):

```console
cd webs3
runapp start
```

Stop deployment/app process:

```console
runapp stop
```

Check running deployment/app process:

```console
runapp list
```

Restart deployment/app process:

```console
runapp restart
```

If app is not running after restart, check & re-deploy:

```console
runapp list
runapp start
```

#### Default Buckets Listing

By default, webs3 will show a listing of all available buckets that are in the S3 account using the `f` parameter in the url. The default value of the `f` parameter is `/` which in this case means list all buckets.

```py
https://localhost:8003/webs3?f=/
```

#### Additional Rendering Options (from [webcsv](https://github.com/ryt/webcsv))

Markdown, RST (reStructuredText), and HTML files can additionally be parsed and rendered using the following options: `parse_markdown`, `parse_rst`, and `parse_html`.

> If you enable the `parse_markdown` option by setting it to `True`, you'll need to install the [marko](https://marko-py.readthedocs.io/en/latest/) library to your python libraries. 

```console
$ pip3 install marko
```

> If you enable the `parse_rst` option by setting it to `True`, you'll need to install the [docutils](https://docutils.sourceforge.io/rst.html) library to your python libraries. 

```console
$ pip3 install docutils
```


### Port Notes

1. When deployed with Gunicorn, the app uses port `8003` by default. You can change this by editing `runapp.conf` as well as `webs3.html`.

2. Flask uses the port `5000` by default for it's development server. Make sure to access the app using that port whenever you're running the flask server.

#### Similar App Recommendations

**Useful Free & Paid S3 Apps for Desktop, Mobile, and Web**

- [Cyberduck](https://cyberduck.io/) by iterate GmbH
- [Mountain Duck](https://mountainduck.io/) by iterate GmbH
- [FileBrowserGO](https://www.stratospherix.com/filebrowsergo/) by Stratospherix
- [Amplify S3 Browser](https://github.com/aws-samples/sample-amplify-storage-browser) React+Vite Web App by AWS



