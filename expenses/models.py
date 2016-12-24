from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import decimal
from decimal import Decimal
from random import shuffle


class Atom(models.Model):
    """
    Model for elemental operation, which contain a user and a signed amount.
    """
    user = models.ForeignKey('ExtendedUser', related_name='atoms')
    amount = models.DecimalField(verbose_name=_("Amount"), max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
    child_of_bill = models.ForeignKey('Bill', related_name='atoms')

    def __str__(self):  # TODO: code actual localisation
        return _("%(user)s: %(amount)s for %(bill)s") % {
            'user': self.user,
            'amount': self.localised_amount(),
            'bill': self.child_of_bill.title,
        }

    def localised_amount(self):
        # TODO
        return "%s €" % (abs(self.amount),)

    class Meta:
        # TODO unique_together ('user', 'child_of_bill', 'amount>0')
        #unique_together = ('user', 'child_of_bill', )
        pass


class Bill(models.Model):
    """
    Model for atoms aggregation. Gives a context and a description to a group of atoms.
    """
    creator = models.ForeignKey('ExtendedUser')
    category = models.ManyToManyField('Category', blank=True)
    amount = models.DecimalField(verbose_name=_("Amount"), max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(verbose_name=_("Title"), max_length=100)
    description = models.TextField(blank=True)
    refund = models.BooleanField(editable=False, default=False)

    def __str__(self):
        return _("%(time)s - %(title)s: %(amount)s €") % {
            'time': self.date.strftime('%c'),
            'title': self.title,
            'amount': self.amount,
        }

    def clean(self, *args, **kwargs):
        """
        Integrity check and hack for empty form (self.atoms.all() == [])
        """
        try:
            self.check_integrity()
        except ValidationError:
            if self.atoms.all():
                raise # Raise the last exception

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

    def refund_name(self):
        """
        Gives the title for a refund bill.
        """
        return _("Repayment: ") + "%s €" % (self.amount,)

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

    def equal_split(self, participants):
        """
        Returns an (almost) equally repartition of expenditures among the
        ``participants`` list. The result is a list of pairs (participant,amount)
        """
        decimal.getcontext().rounding = decimal.ROUND_DOWN
        nb_of_participants = len(participants)
        missing_cents = int(self.amount*100 % nb_of_participants)
        base_amount = (-self.amount/nb_of_participants).quantize(Decimal('.01'))
        amount_list = [base_amount - Decimal('0.01')]*missing_cents
        amount_list += [base_amount]*(nb_of_participants - missing_cents)
        shuffle(amount_list)
        return zip(participants, amount_list)

    def create_atoms(self, buyer, participants, is_refund=False):
        """
        Creates the list of atoms from one ```buyer``` to ```participants``` by equal split method.
        If the amount is not a number of ```participants``` multiple, gives the remaining cents to random ```participants```.
        """
        if is_refund:
            participant_atom = Atom()
            participant_atom.user = participants
            participant_atom.amount = -self.amount
            participant_atom.child_of_bill = self
            participant_atom.save()
        else:
            for participant, amount in amount_list:
                participant_atom = Atom()
                participant_atom.amount = amount
                participant_atom.user = participant
                participant_atom.child_of_bill = self
                participant_atom.save()

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

    def list_of_participants(self):
        """
        Returns the list of participants for the current ```Bill``` instance.
        """
        return [atom.user for atom in self.list_of_negative_atoms()]

    def list_of_people_involved(self):
        """
        Returns the list of user involved in the current ```Bill``` instance.
        """
        return list(set(self.list_of_buyers() + self.list_of_participants()))

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
    nickname = models.CharField(max_length=20, help_text="name to be displayed")

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

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.user.username
        return super().save(*args, **kwargs)


class Category(models.Model):
    """
    An attribute that can be shared by both ```Bill and ```ExtendedUser``` instances.
    Will be used in the future.
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
