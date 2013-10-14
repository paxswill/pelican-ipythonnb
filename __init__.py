import os
from pelican import signals

try:
    from pelican.readers import BaseReader  # new Pelican API
except ImportError:
    from pelican.readers import Reader as BaseReader

try:
    from pelican.readers import EXTENSIONS  # old Pelican API
except ImportError:
    EXTENSIONS = None

try:
    import json
    import markdown

    from IPython.config import Config
    from IPython.nbconvert.exporters import HTMLExporter
except Exception as e:
    IPython = False
    raise e


class iPythonNB(BaseReader):
    enabled = True
    file_extensions = ['ipynb']

    def read(self, filepath):
        filedir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        _metadata = {}
        # See if metadata file exists metadata
        metadata_filename = filename.split('.')[0] + '.ipynb-meta'
        metadata_filepath = os.path.join(filedir, metadata_filename)
        if os.path.exists(metadata_filepath):
            with open(metadata_filepath, 'r') as metadata_file:
                content = metadata_file.read()
                metadata_file = open(metadata_filepath)
                md = markdown.Markdown(extensions=['meta'])
                md.convert(content)
                _metadata = md.Meta

            for key, value in _metadata.items():
                _metadata[key] = value[0]
        else:
            # Try to load metadata from inside ipython nb
            ipynb_file = open(filepath)
            _metadata = json.load(ipynb_file)['metadata']

        metadata = {}
        for key, value in _metadata.items():
            key = key.lower()
            metadata[key] = self.process_metadata(key, value)
        metadata['ipython'] = True

        # Converting ipythonnb to html
        config = Config({'CSSHTMLHeaderTransformer': {'enabled': True}})
        exporter = HTMLExporter(config=config, template_file='basic')
        body, info = exporter.from_filename(filepath)

        return body, metadata


def add_reader(arg):
    if EXTENSIONS is None:  # new pelican API:
        arg.settings['READERS']['ipynb'] = iPythonNB
    else:
        EXTENSIONS['ipynb'] = iPythonNB


def register():
    signals.initialized.connect(add_reader)
