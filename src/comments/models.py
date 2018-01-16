from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models


class CommentManager(models.Manager):
    def all(self):
        qs = super(CommentManager, self).filter(parent=None)
        return qs

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id

        qs = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).filter(parent=None)

        return qs


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey("self", null=True, blank=True)

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = CommentManager()

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        return True if self.parent else False

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('comments:thread', kwargs={'id': self.id})

    def get_delete_url(self):
        return reverse('comments:delete', kwargs={'id': self.id})

    class Meta:
        ordering = ["-timestamp"]
