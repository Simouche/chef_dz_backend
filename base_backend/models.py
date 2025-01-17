from django.db import models
from django.db.models import Func

do_nothing = models.DO_NOTHING
cascade = models.CASCADE


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DeletableModel(BaseModel):
    visible = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Round(Func):
    def __ror__(self, other):
        pass

    def __rand__(self, other):
        pass

    function = 'ROUND'
    arity = 2
