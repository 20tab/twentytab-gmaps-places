from django.db import models
from gmapsplaces.models import GmapsPlace


# Create your models here.
class TestPlace(models.Model):
    location = models.ForeignKey(GmapsPlace)

    def __unicode__(self):
        return u"{}".format(self.location)
