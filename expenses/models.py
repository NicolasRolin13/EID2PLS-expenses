from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import decimal
from decimal import Decimal


class Atom(models.Model):
    """
    Model for elemental operation, which contain a user and a signed amount.
    """
    user = models.ForeignKey('ExtendedUser', related_name='atoms')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    child_of_bill = models.ForeignKey('Bill', related_name='atoms')

    def __str__(self):  # TODO: code actual localisation
        return "%s: %s for %s" % (self.user, self.localised_amount(), self.child_of_bill.title)

    def localised_amount(self):
        return "€%s" % (self.amount)


class Bill(models.Model):
    """
    Model for atoms aggregation. Gives a context and a description to a group of atoms.
    """
    creator = models.ForeignKey('ExtendedUser')
    category = models.ManyToManyField('Category', blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    repayment = models.BooleanField(editable=False, default=False)

    def __str__(self):
        return "%s - %s (%s€)" % (self.date.strftime('%c'), self.title, self.amount)

    def clean(self, *args, **kwargs):
        try:
            self.check_integrity()
        except ValidationError:
            if self.atoms.all():
                raise

    def check_integrity(self):
        """
        Checks if the amount of the ```Bill``` instance match the sum of his atoms amount.
        Useful to check if some atoms were modified manually.
        """
        is_equal = self.calculate_positive_amount() == self.amount
        is_null = (self.calculate_positive_amount() + self.calculate_negative_amount()) == 0
        return is_equal and is_null

    @classmethod
    def check_global_integrity(cls):
        """
        Integrity check of all instances of ```Bill``` model.
        """
        return [failure for failure in cls.objects.all() if not failure.check_integrity()]

    def repayment_name(self):
        """
        Gives the title for a repayment bill.
        """
        return "Repayment: €%s" % (self.amount)

    def calculate_positive_amount(self):
        """
        Calculates the sum of positive atoms of a ```Bill``` instance.
        """
        return sum(atom.amount for atom in self.atoms.all() if atom.amount > 0)

    def calculate_negative_amount(self):
        """
        Calculates the sum of negative atoms of a ```Bill``` instance.
        """
        return sum(atom.amount for atom in self.atoms.all() if atom.amount < 0)

    def update_amount(self):
        """
        Updates the field ```amount``` with the sum of positive atoms amount.
        """
        self.amount = self.calculate_positive_amount()

    def equal_split(self, receivers):
            decimal.getcontext().rounding = decimal.ROUND_DOWN
            receivers = receivers.order_by('?')
            nb_of_receivers = len(receivers)
            missing_cents = self.amount*100 % nb_of_receivers
            amount_list = []
            for i, receiver in enumerate(receivers):
                if i < missing_cents:
                    amount_list.append((receiver , ((-self.amount/nb_of_receivers) - Decimal(0.01)).quantize(Decimal('.01'))))
                else:
                    amount_list.append((receiver, (-self.amount/nb_of_receivers).quantize(Decimal('.01'))))
            return amount_list

    def create_atoms(self, buyer, receivers, is_repayment=False):
        """
        Creates the list of atoms from one ```buyer``` to ```receivers``` by equal split method.
        If the amount is not a number of ```receivers``` multiple, gives the remaining cents to random ```receivers```.
        """
        if is_repayment:
            receiver_atom = Atom()
            receiver_atom.user = receivers
            receiver_atom.amount = -self.amount
            receiver_atom.child_of_bill = self
            receiver_atom.save()
        else:
            for receiver, amount in amount_list:
                receiver_atom = Atom()
                receiver_atom.amount = amount
                receiver_atom.user = receiver
                receiver_atom.child_of_bill = self
                receiver_atom.save()

        buyer_atom = Atom()
        buyer_atom.amount = self.amount
        buyer_atom.user = buyer
        buyer_atom.child_of_bill = self
        buyer_atom.save()

    def list_of_positive_atoms(self):
        """
        Returns the list of atoms with a positive amount for the current ```Bill``` instance.
        """
        return [atom for atom in self.atoms.all() if atom.amount > 0]

    def list_of_negative_atoms(self):
        """
        Returns the list of atoms with a negative amount for the current ```Bill``` instance.
        """
        return [atom for atom in self.atoms.all() if atom.amount < 0]

    def list_of_buyers(self):
        """
        Returns the list of buyers for the current ```Bill``` instance.
        """
        return [atom.user for atom in self.list_of_positive_atoms()]

    def list_of_receivers(self):
        """
        Returns the list of receivers for the current ```Bill``` instance.
        """
        return [atom.user for atom in self.list_of_negative_atoms()]

    def list_of_people_involved(self):
        """
        Returns the list of user involved in the current ```Bill``` instance.
        """
        return list(set(self.list_of_buyers() + self.list_of_receivers()))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (not exc_type and not self.atoms.all()) or (exc_type == ValidationError):
            self.delete()


class ExtendedUser(models.Model):
    """
    Extension of Django's User model with a one to one link.
    """
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=20)

    @property
    def balance(self):
        """
        Calculates the balance of the current ```ExtendedUser``` instance.
        """
        return sum([atom.amount for atom in self.atoms.all()])

    def __str__(self):
        return self.nickname

    def __lt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) == int:
                return self.balance < other
            else:
                return self.balance < other.balance
        else:
            return NotImplemented

    def __le__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) == int:
                return self.balance <= other
            else:
                return self.balance <= other.balance
        else:
            return NotImplemented

    def __eq__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) == int:
                return self.balance == other
            else:
                return self.balance == other.balance
        else:
            return NotImplemented

    def __ne__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) == int:
                return self.balance != other
            else:
                return self.balance != other.balance
        else:
            return NotImplemented

    def __gt__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) == int:
                return self.balance > other
            else:
                return self.balance > other.balance
        else:
            return NotImplemented

    def __ge__(self, other):
        if type(self) == type(other) or type(other) == int:
            if type(other) == int:
                return self.balance >= other
            else:
                return self.balance >= other.balance
        else:
            return NotImplemented


class Category(models.Model):
    """
    An attribute that can be shared by both ```Bill and ```ExtendedUser``` instances.
    Will be used in the future.
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
