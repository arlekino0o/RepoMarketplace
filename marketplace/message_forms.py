from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'repository']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a message...'}),
        }
