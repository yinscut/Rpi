from django.db import models
from django.contrib.auth.models import User

class ListTextField(models.TextField):
    def get_prep_value(self, value):
        if not value:
            return ''
        else:
            return ','.join(value)
    def to_python(self, value):
        if not value:
            return []
        else:
            return value.split(',')
    def from_db_value(self,value,expression,connection,context):
        if not value:
            return []
        else:
            return value.split(',')

class dc_data(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    uid = models.CharField(max_length=30,unique=True)
    name = models.CharField(max_length=30,default='noname')

    breakfast_book = ListTextField(default=[])
    lunch_book = ListTextField(default=[])
    dinner_book = ListTextField(default=[])
    breakfast_eat = ListTextField(default=[])
    lunch_eat = ListTextField(default=[])
    dinner_eat = ListTextField(default=[])
    other_eat = ListTextField(default=[])

    def __str__(self):
        return self.user.username