from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    disabled_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class Domain(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    qr_code = models.CharField(max_length=1000)


class Visit(BaseModel):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, blank=True, null=True)