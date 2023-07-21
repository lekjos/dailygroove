from django import forms


class PlayerInviteForm(forms.Form):
    recipient_email = forms.EmailField()
