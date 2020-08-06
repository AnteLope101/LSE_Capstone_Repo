from scrapy.exporters import CsvItemExporter
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

class MyCsvItemExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):

        # args[0] is (opened) file handler
        # if file is not empty then skip headers
        if args[0].tell() > 0:
            kwargs['include_headers_line'] = False
        
        kwargs['fields_to_export'] = settings.getlist('EXPORT_FIELDS') or None
        kwargs['encoding'] = settings.get('EXPORT_ENCODING', 'utf-8')

        super(MyCsvItemExporter, self).__init__(*args, **kwargs)