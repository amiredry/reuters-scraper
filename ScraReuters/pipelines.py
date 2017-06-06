# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.contrib.exporter import XmlItemExporter


class XmlExportPipeline(object):
    count = 0

    def __init__(self):
        self.exporter = None
        self.outdir = None
        self.file = None

    def process_item(self, item, spider):

        XmlExportPipeline.count += 1
        self.outdir = spider.date.strftime('%Y%m%d')
        self.file = open('reuters/%s/%s_item.xml' % (self.outdir, XmlExportPipeline.count), 'w+b')
        self.exporter = XmlItemExporter(self.file, root_element='items', item_element='story')

        self.exporter.start_exporting()
        self.exporter.export_item(item)
        self.exporter.finish_exporting()
        return item