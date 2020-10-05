from django.db import models

# Create your models here.
from base_backend.models import BaseModel


class TermsAndConditions(BaseModel):
    terms = models.TextField()

    def __str__(self):
        return self.terms
