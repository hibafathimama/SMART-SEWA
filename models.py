from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class staff_table(models.Model):
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    gender=models.CharField(max_length=10)
    dob=models.DateField()
    phoneno=models.BigIntegerField()
    email=models.CharField(max_length=50)
    photo=models.FileField()

class user_table(models.Model):
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    gender=models.CharField(max_length=10)
    dob=models.DateField()
    phoneno=models.BigIntegerField()
    email=models.CharField(max_length=50)
    photo=models.FileField()
    place=models.CharField(max_length=100)
    post=models.CharField(max_length=100)
    pin=models.IntegerField()

class rules_table(models.Model):
    rules=models.CharField(max_length=100)
    details=models.CharField(max_length=200)
    date=models.DateField()

class service_table(models.Model):
    service=models.CharField(max_length=100)
    details=models.CharField(max_length=200)
    date=models.DateField()
    cost= models.IntegerField()
    time=models.IntegerField()


class service_document_table(models.Model):
    SERVICE = models.ForeignKey(service_table,on_delete=models.CASCADE)
    details = models.CharField(max_length=200)
    document = models.FileField()

class dataset_table(models.Model    ):
    question=models.CharField(max_length=200)
    answer=models.CharField(max_length=200)

class booking_table(models.Model):
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    status=models.CharField(max_length=100)
    date=models.DateField()
    amount= models.IntegerField()

class booking_details_table(models.Model):
    BOOKING=models.ForeignKey(booking_table,on_delete=models.CASCADE)
    SERVICE=models.ForeignKey(service_table,on_delete=models.CASCADE)
    status = models.CharField(max_length=100)

class staff_timing(models.Model):
    BOOKING=models.ForeignKey(booking_table,on_delete=models.CASCADE,default=1)
    STAFF=models.ForeignKey(staff_table,on_delete=models.CASCADE)
    start_time = models.CharField(max_length=100,null=True,blank=True)
    end_time = models.CharField(max_length=100, null=True,blank=True)

class document_table(models.Model):
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    document = models.FileField()
    title = models.CharField(max_length=100)
    date = models.DateField()

class leave_table(models.Model):
    STAFF=models.ForeignKey(staff_table,on_delete=models.CASCADE)
    reason = models.CharField(max_length=500)
    status = models.CharField(max_length=100)
    appldate = models.DateField()
    fromdate = models.DateField()
    todate = models.DateField()


class feedback_table(models.Model):
    USER = models.ForeignKey(user_table, on_delete=models.CASCADE)
    STAFF=models.ForeignKey(staff_table,on_delete=models.CASCADE)
    feedback = models.CharField(max_length=500)
    rating = models.FloatField()
    date = models.DateField()

class notification_table(models.Model):
    STAFF=models.ForeignKey(staff_table,on_delete=models.CASCADE)
    notification= models.CharField(max_length=500)
    details = models.CharField(max_length=200)
    date = models.DateField()

class user_chatbot_table(models.Model):
    USER = models.ForeignKey(user_table, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    date = models.DateField()

class Complaint_table(models.Model):
    USER = models.ForeignKey(user_table, on_delete=models.CASCADE)
    complaint = models.CharField(max_length=200)
    reply = models.CharField(max_length=200)
    status = models.CharField(max_length=200,default="pending")
    date = models.DateField()


class Chatbot(models.Model):
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE,default='')
    date=models.DateField()
    question=models.TextField()
    answer=models.TextField()

