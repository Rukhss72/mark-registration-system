from django.db import models

# Create your models here.

class Marks(models.Model):
    module_code = models.CharField(max_length=20)
    module_name = models.CharField(max_length=100)
    cw1_marks = models.IntegerField()
    cw2_marks = models.IntegerField()
    cw3_marks = models.IntegerField()
    student_id = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    date_of_entry = models.DateField()

    def __str__(self):
        return f"{self.student_name} - {self.module_code}"
