from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Transfer(models.Model):
    '''
    Simple model for transfering currency from one person to another.
    The transfer instance should never be created or modified manually.
    '''
    sender = models.ForeignKey('ExtendedUser', related_name='senders')
    receiver = models.ForeignKey('ExtendedUser', related_name='receivers')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    child_of_bill = models.ForeignKey('Bill', related_name='transfers')

    def __str__(self):
        return "%s --> %s (%s€)" % (self.sender, self.receiver, self.amount)

class Bill(models.Model):
    '''
    Model for transfers aggregation. Give a context and a description to a group of transfers.
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
        Calculate the sum of transfers amount of a Bill instance.
        '''
        return sum(transfer.amount for transfer in self.transfers.all())

    def update_amount(self):
        '''
        Update the field amount with the sum of transfers amount.
        '''
        self.amount = self.calculate_amount()

    def check_integrity(self):
        '''
        Check if the amount of the Bill instance match the sum of his transfers amount.
        Useful to check if some transfers were modified manually.
        '''
        return self.calculate_amount() == self.amount

    def create_transfers(self, buyer, receivers):
        '''
        Create the list of transfers from one buyer to receivers by equal split method.
        '''
        for receiver in receivers:
            transfer = Transfer()
            transfer.amount = self.amount/len(receivers)
            transfer.sender = buyer
            transfer.receiver = receiver
            transfer.child_of_bill = self
            transfer.save()

    def list_of_senders(self):
        return [transfer.sender for transfer in self.transfers.all()]

    def list_of_receivers(self):
        return [transfer.receiver for transfer in self.transfers.all()]

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
        Used for bootstraping the registration of transfers.
        '''
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.check_integrity():
            raise ValidationError("Current amount doesn't match the sum of transfers amounts")
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s - %s (%s€)" % (self.date.strftime('%c'), self.title, self.amount)

class ExtendedUser(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0)

    def calculate_balance(self):
        positive = sum(transfer.amount for transfer in self.senders.all())
        negative = sum(transfer.amount for transfer in self.receivers.all())
        return (positive - negative)

    def update_amount(self):
        '''
        Update the field balance with the sum of transfers amount.
        '''
        self.balance = self.calculate_balance()

    def check_integrity(self):
        '''
        Check if the balance of the ExtendedUser instance match the sum of his transfers amount.
        Useful to check if some transfers were modified manually.
        '''
        return self.calculate_balance() == self.balance

    @classmethod
    def check_global_integrity(cls):
        '''
        Integrity check of all instances of ExtendedUser model.
        '''
        return [failure for failure in cls.objects.all() if not failure.check_integrity()]

    def __str__(self):
        return self.nickname

    def __lt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance < other
            else:
                return self.balance < other.balance
        else:
            return TypeError

    def __le__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance <= other
            else:
                return self.balance <= other.balance
        else:
            return TypeError

    def __eq__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance == other
            else:
                return self.balance == other.balance
        else:
            return TypeError

    def __ne__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance != other
            else:
                return self.balance != other.balance
        else:
            return TypeError

    def __gt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance > other
            else:
                return self.balance > other.balance
        else:
            return TypeError

    def __lt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance >= other
            else:
                return self.balance >= other.balance
        else:
            return TypeError

class Category(models.Model):
    '''
    Just an attribute that can be shared by both Bill and User instances.
    Will be used in the future.
    '''
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
