import shortuuid
from django.db import models
from django.utils import timezone

# Create your models here.
def create_uuid():
    return shortuuid.uuid()


class Base(models.Model):
    unified_uuid = models.CharField(
        "统一UUID标识",
        default=create_uuid,
        unique=True,
        editable=False,
        db_index=True,
        max_length=25
    )
    uuid = models.CharField(
        primary_key=True,
        default=create_uuid,
        editable=False,
        verbose_name='ID',
        max_length=25
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('修改时间', auto_now=True)
    is_deleted = models.BooleanField("是否删除", default=False, db_index=True)
    deleted_at = models.DateTimeField('删除时间', null=True, blank=True)

    class Meta:
        abstract = True

    # ✅ 软删除方法
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    # ✅ 恢复方法
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
