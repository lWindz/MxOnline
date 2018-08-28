# coding:utf-8

import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from django.template import loader
from xadmin.plugins.utils import get_context_dict


# excel 导入
class ListImportExcelPlugin(BaseAdminPlugin):
    import_excel = True

    # 确定是否加载插件
    def init_request(self, *args, **kwargs):
        return bool(self.import_excel)

    # 将自定义的html页面显示在xamdin上
    def block_top_toolbar(self, context, nodes):
        nodes.append(loader.render_to_string('xadmin/excel/model_list.top_toolbar.import.html',
                                             context=get_context_dict(context)))


xadmin.site.register_plugin(ListImportExcelPlugin, ListAdminView)
