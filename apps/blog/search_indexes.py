from haystack import site
from search import indexes
from blog.models import Post

class PostIndex(indexes.search_class()):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    body = indexes.CharField(model_attr='text')
    date = indexes.DateField(model_attr='date')
    is_draft = indexes.BooleanField(model_attr='is_draft')

    def get_queryset(self):
        return Post.objects.all()

site.register(Post, PostIndex)

