from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Transfert(models.Model):
    '''
    Simple model for transfering currency from one person to another.
    The transfert instance should never be created or modified manually.
    '''
    sender = models.ForeignKey('ExtendedUser', related_name='senders')
    receiver = models.ForeignKey('ExtendedUser', related_name='receivers')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    child_of_bill = models.ForeignKey('Bill', related_name='transferts')

    def __str__(self):
        return "%s --> %s (%s€)" % (self.sender, self.receiver, self.amount)

class Bill(models.Model):
    '''
    Model for transferts aggregation. Give a context and a description to a group of transferts.
    '''
    creator = models.ForeignKey('ExtendedUser')
    category = models.ManyToManyField('Category')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    repayment = models.BooleanField(editable=False, default=False)

    def calculate_amount(self):
        '''
        Calculate the sum of transferts amount of a Bill instance.
        '''
        return sum(transfert.amount for transfert in self.transferts.all())

    def update_amount(self):
        '''
        Update the field amount with the sum of transferts amount.
        '''
        self.amount = self.calculate_amount()

    def check_integrity(self):
        '''
        Check if the amount of the Bill instance match the sum of his transferts amount.
        Useful to check if some transferts were modified manually.
        '''
        return self.calculate_amount() == self.amount

    def create_transferts(self, buyer, receivers):
        '''
        Create the list of transferts from one buyer to receivers by equal split method.
        '''
        for receiver in receivers:
            transfert = Transfert()
            transfert.amount = self.amount/len(receivers)
            transfert.sender = buyer
            transfert.receiver = receiver
            transfert.child_of_bill = self
            transfert.save()

    def list_of_senders(self):
        return [transfert.sender for transfert in self.transferts.all()]

    def list_of_receivers(self):
        return [transfert.receiver for transfert in self.transferts.all()]

    def list_of_people_involved(self):
        return list(set(self.list_of_senders() + self.list_of_receivers()))

    @classmethod
    def check_global_integrity(cls):
        '''
        Integrity check of all instances of Bill model.
        '''
        return [failure for failure in cls.objects.all() if not failure.check_integrity()]

    def unsafe_save(self, *args, **kwargs):
        '''
        Register the instance to SQL database without integrity check.
        Used for bootstraping the registration of transferts.
        '''
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.check_integrity():
            raise ValidationError("Current amount doesn't match the sum of transferts amounts")
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s - %s (%s€)" % (self.date.strftime('%c'), self.title, self.amount)

class ExtendedUser(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=20)

    def calculate_balance(self):
        positive = sum(transfert.amount for transferts in self.senders.all())
        negative = sum(transfert.amount for transferts in self.receivers.all())
        return (positive - negative)

    def __str__(self):
        return self.nickname

class Category(models.Model):
    '''
    Just an attribute that can be shared by both Bill and User instances.
    Will be used in the future.
    '''
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
