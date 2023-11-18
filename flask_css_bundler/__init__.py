from hashlib import md5
from typing import List

class CSSBundler:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        self.stylesheet_tag = app.config.get(
            'CSS_BUNDLER_CUSTOM_TAG',
            '<link rel="stylesheet" href="{stylesheet}">'
        )

        self.dont_use_bundle = app.config.get(
            'CSS_BUNDLER_DONT_USE_BUNDLE',
            False
        )

        self.css_files_path = app.config.get(
            'CSS_BUNDLER_CSS_FILES_PATH',
            '/static/css/'
        )

        self.bucket_url = app.config.get(
            'CSS_BUNDLER_BUCKET_URL'
        )

        self.use_bucket_url = app.config.get(
            'CSS_BUNDLER_USE_BUCKET_URL',
            False
        )

        self.stop_generating = app.config.get(
            'CSS_BUNDLER_STOP_GENERATING',
            False
        )

        if self.bucket_url is not None and self.bucket_url[-1] != '/':
            self.bucket_url += '/'

    def init_app(self, app):
        app.jinja_env.globals.update(
            CSSBUNDLE=self.__bundler
        )

    def generate_bundle_filename(self, stylesheets: List[str]) -> str:
        _hash = md5()

        for stylesheet in stylesheets:
            _hash.update(stylesheet.encode())

        return _hash.hexdigest()[:12] + '.css'
    
    def generate_bundled_css(self, bundle_filename: str, stylesheets: List[str]) -> None:
        bundled_css = b''

        for stylesheet in stylesheets:
            with open(stylesheet[1:], 'rb') as css_file:
                bundled_css += css_file.read() + b'\n'

        with open(self.css_files_path[1:] + bundle_filename, 'wb') as bundled_file:
            bundled_file.write(bundled_css)
    
    def __prepare_stylesheet(self, custom_paths: dict, stylesheets: dict) -> str:
        prepared_stylsheets = []

        for stylesheet in stylesheets:
            if (custom_path := custom_paths.get(stylesheet)) is not None:
                custom_path = custom_path.replace('\\', '')
                
                if custom_path[-1] != '/':
                    custom_path += '/'

                stylesheet = custom_path + stylesheet
            else:
                stylesheet = self.css_files_path + stylesheet

            if '.css' not in stylesheet:
                stylesheet += '.css'

            prepared_stylsheets.append(stylesheet)

        return prepared_stylsheets

    def __bundler(self, *args, custom_paths: dict = {}):
        stylesheets = self.__prepare_stylesheet(
            custom_paths=custom_paths,
            stylesheets=args
        )

        if self.dont_use_bundle is True:
            stylesheets = map(
                lambda stylesheet: self.stylesheet_tag.format(stylesheet=stylesheet),
                stylesheets
            )

            return stylesheets
        
        bundle_filename = self.generate_bundle_filename(
            stylesheets=stylesheets
        )

        if self.stop_generating is False:
            self.generate_bundled_css(
                bundle_filename=bundle_filename,
                stylesheets=stylesheets
            )

        if self.bucket_url is not None and self.use_bucket_url is True:
            bundled_stylesheets = self.bucket_url + bundle_filename
        else:
            bundled_stylesheets = self.css_files_path + bundle_filename

        return [self.stylesheet_tag.format(stylesheet=bundled_stylesheets)]