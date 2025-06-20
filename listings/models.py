from django.db import models
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.validators import MinValueValidator
from django.urls import reverse


s3 = S3Boto3Storage()


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Listing(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.
                             CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                 null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price_per_night = models.PositiveIntegerField()
    is_accessible = models.BooleanField(default=False)
    dog_policy = models.TextField(blank=True)
    max_dogs = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of dogs allowed"
    )
    image = models.ImageField(
        storage=s3,
        upload_to="listings/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """
        Returns the canonical URL to view this listing’s detail page.
        """
        return reverse("listings:listing_detail", args=[self.pk])