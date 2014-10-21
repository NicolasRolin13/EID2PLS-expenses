from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Transfert(models.Model):
    sender = models.ForeignKey('ExtendedUser', related_name='senders')
    receiver = models.ForeignKey('ExtendedUser', related_name='receivers')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    child_of_bill = models.ForeignKey('Bill', related_name='transferts')

    def __str__(self):
        return "%s --> %s (%s€)" % (self.sender, self.receiver, self.amount)

class Bill(models.Model):
    creator = models.ForeignKey('ExtendedUser')
    category = models.ManyToManyField('Category')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    repayment = models.BooleanField(editable=False, default=False)

    def calculate_amount(self):
        transferts_sum = 0
        for transfert in self.transferts:
            transferts_sum += transfert.amount
        return sum

    def update_amount(self):
        self.amount = calculate_amount()

    def check_integrity(self):
        return calculate_amount == amount

    def create_transferts(self, buyer, receivers):
        for receiver in receivers:
            transfert = Transfert()
            transfert.amount = self.amount/len(receivers)
            transfert.sender = buyer
            transfert.receiver = receiver
            child_of_bill = self

            transfert.save()

    @classmethod
    def check_global_integrity(cls):
        return [failure for failure in cls.objects.all() if not failure.check_integrity()]

    def unsafe_save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not check_integrity:
            raise ValidationError("Current amount doesn't match the sum of transferts amounts")
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s - %s (%s€)" % (self.date, self.title, self.amount)

class ExtendedUser(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=20)

    def __str__(self):
        return self.nickname

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
