# 定义索引类
from haystack import indexes
# 导入模型类
from Essay.models import Essay


class EssayIndex(indexes.SearchIndex, indexes.Indexable):
    # 索引字段
    # use_template指定根据表中的哪些字段建立索引文件，把说明放在一个文件中
    text = indexes.CharField(document=True, use_template=True)

    title = indexes.CharField(model_attr='title')   #创建一个字段  
    content = indexes.CharField(model_attr='content')   #创建一个字段  

    def get_model(self):
        # 返回模型类
        return Essay
    
    def index_queryset(self, using=None):
        # 建立索引数据
        return self.get_model().objects.all()

