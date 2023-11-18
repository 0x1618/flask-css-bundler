from hashlib import md5
from typing import List
import re
import glob

class CSSBundler:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.globals.update(
            CSSBUNDLE=self.__bundler
        )

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

        self.bundles_folder = app.config.get(
            'CSS_BUNDLER_BUNDLES_FOLDER',
            ''
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

        self.templates_path = app.config.get(
            'CSS_BUNDLER_TEMPLATES_PATH',
            'templates/'
        )

        if self.bucket_url is not None and self.bucket_url[-1] != '/':
            self.bucket_url += '/'

        self.bundles_folder.replace('\\', '')
        self.css_files_path.replace('\\', '')
        self.templates_path.replace('\\', '')

        if self.templates_path is not None and self.templates_path[-1] != '/':
            self.templates_path += '/'

        if self.bundles_folder != '' and self.bundles_folder[-1] != '/':
            self.bundles_folder += '/'
            
            if self.bundles_folder[0] == '/':
                self.bundles_folder = self.bundles_folder[1:]

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

        bundle_path = self.css_files_path[1:] + self.bundles_folder + bundle_filename

        with open(bundle_path, 'wb') as bundled_file:
            bundled_file.write(bundled_css)

    def generate_all_bundles(self):
        pattern = re.compile(r'.*CSSBUNDLE\(([\s\S]*?)\)')
        html_files = glob.glob(f'{self.templates_path}**/*.html', recursive=True)

        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as file:
                content = file.read()
                args = re.findall(pattern, content)

                if len(args) > 0:
                    args = ''.join(args).split(',')
                    args = list(map(lambda arg: arg.replace("'", '').replace('"', '').replace(' ', '').replace('\n', ''), args))
                    print(args)
                    self.__process_bundling(*args, custom_paths={})
    
    def __prepare_stylesheet(self, custom_paths: dict, stylesheets: List[str]) -> str:
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

    def __process_bundling(self, *args, custom_paths: dict = {}):
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
            bundled_stylesheets = self.css_files_path + self.bundles_folder + bundle_filename

        return [self.stylesheet_tag.format(stylesheet=bundled_stylesheets)]

    def __bundler(self, *args, custom_paths: dict = {}):
        return self.__process_bundling(*args, custom_paths=custom_paths)