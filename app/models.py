from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    disabled_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class Domain(BaseModel):
    name = models.CharField(max_length=255)
    qr_code = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = ('name', 'user',)


class Visit(BaseModel):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, blank=True, null=True)