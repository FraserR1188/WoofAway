# custom_storages.py

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = settings.STATICFILES_LOCATION  # prefix in your bucket, e.g. "static"
    default_acl = 'public-read'
    file_overwrite = True
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
