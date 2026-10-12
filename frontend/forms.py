from django import forms

from drivers.models import Driver
from shipments.models import Shipment


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ShipmentCreateForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            "sender_name",
            "receiver_name",
            "pickup_address",
            "delivery_address",
        ]

        widgets = {
            "sender_name": forms.TextInput(
                attrs={"placeholder": "Sender name"}
            ),
            "receiver_name": forms.TextInput(
                attrs={"placeholder": "Receiver name"}
            ),
            "pickup_address": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Pickup address"}
            ),
            "delivery_address": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Delivery address"}
            ),
        }


class AssignDriverForm(forms.Form):
    driver = forms.ModelChoiceField(
        queryset=Driver.objects.filter(is_available=True),
        empty_label="Select available driver",
    )


class ShipmentStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=Shipment.STATUS_CHOICES
    )