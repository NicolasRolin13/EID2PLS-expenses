from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Atom(models.Model):
    user = models.ForeignKey('ExtendedUser', related_name='atoms')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    child_of_bill = models.ForeignKey('Bill', related_name='atoms')

    def __str__(self):
        return "%s: %s for %s" % (self.user, self.localised_amount(), self.child_of_bill.title)

    def localised_amount(self):
        return "€%s" % (self.amount)
class Bill(models.Model):
    '''
    Model for atoms aggregation. Give a context and a description to a group of atoms.
    '''
    creator = models.ForeignKey('ExtendedUser')
    category = models.ManyToManyField('Category', blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    repayment = models.BooleanField(editable=False, default=False)

    def calculate_positive_amount(self):
        '''
        Calculates the sum of positive atoms of a Bill instance.
        '''
        return sum(atom.amount for atom in self.atoms.all() if atom.amount > 0)

    def calculate_negative_amount(self):
        '''
        Calculates the sum of negative atoms of a Bill instance.
        '''
        return sum(atom.amount for atom in self.atoms.all() if atom.amount < 0)

    def update_amount(self):
        '''
        Update the field amount with the sum of positive atoms amount.
        '''
        self.amount = self.calculate_positive_amount()

    def check_integrity(self):
        '''
        Check if the amount of the Bill instance match the sum of his atoms amount.
        Useful to check if some atoms were modified manually.
        '''
        return self.calculate_positive_amount() == self.amount and (self.calculate_positive_amount() + self.calculate_negative_amount()) == 0

    def create_atoms(self, buyer, receivers):
        '''
        Create the list of atoms from one buyer to receivers by equal split method.
        '''
        for receiver in receivers:
            receiver_atom = Atom()
            receiver_atom.amount = -self.amount/len(receivers)
            receiver_atom.user = receiver
            receiver_atom.child_of_bill = self
            receiver_atom.save()

        buyer_atom = Atom()
        buyer_atom.amount = self.amount
        buyer_atom.user = buyer
        buyer_atom.child_of_bill = self
        buyer_atom.save()

    def list_of_positive_atoms(self):
        return [atom for atom in self.atoms.all() if atom.amount > 0]

    def list_of_negative_atoms(self):
        return [atom for atom in self.atoms.all() if atom.amount < 0]

    def list_of_buyers(self):
        return [atom.user for atom in self.list_of_positive_atoms()]

    def list_of_receivers(self):
        return [atom.user for atom in self.list_of_negative_atoms()]

    def list_of_people_involved(self):
        return list(set(self.list_of_buyers() + self.list_of_receivers()))

    def repayment_name(self):
        return "Repayment: €%s" % (self.amount)

    @classmethod
    def check_global_integrity(cls):
        '''
        Integrity check of all instances of Bill model.
        '''
        return [failure for failure in cls.objects.all() if not failure.check_integrity()]

    def unsafe_save(self, *args, **kwargs):
        '''
        Register the instance to SQL database without integrity check.
        Used for bootstraping the registration of atoms.
        '''
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.check_integrity():
            raise ValidationError("Current amount doesn't match the sum of atoms amounts")
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s - %s (%s€)" % (self.date.strftime('%c'), self.title, self.amount)

class ExtendedUser(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=20)

    @property
    def balance(self):
        return sum([atom.amount for atom in self.atoms.all()])

    def __str__(self):
        return self.nickname

    def __lt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance < other
            else:
                return self.balance < other.balance
        else:
            return NotImplemented

    def __le__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance <= other
            else:
                return self.balance <= other.balance
        else:
            return NotImplemented

    def __eq__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance == other
            else:
                return self.balance == other.balance
        else:
            return NotImplemented

    def __ne__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance != other
            else:
                return self.balance != other.balance
        else:
            return NotImplemented

    def __gt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance > other
            else:
                return self.balance > other.balance
        else:
            return NotImplemented

    def __lt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) ==  int:
                return self.balance >= other
            else:
                return self.balance >= other.balance
        else:
            return NotImplemented

class Category(models.Model):
    '''
    Just an attribute that can be shared by both Bill and User instances.
    Will be used in the future.
    '''
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
