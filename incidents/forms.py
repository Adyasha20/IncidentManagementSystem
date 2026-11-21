from django import forms
from .models import Attachment, Comment, Incident


class IncidentForm(forms.ModelForm):

    class Meta:
        model = Incident

        fields = [
            "title",
            "description",
            "category",
            "priority",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5}
            ),
        }


class AdminIncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['assigned_to', 'category', 'priority', 'deadline']
        widgets = {'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = self.fields['assigned_to'].queryset.filter(role='AGENT')


class AgentUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['status']

    def clean_status(self):
        status = self.cleaned_data['status']
        if status not in ('IN_PROGRESS', 'RESOLVED'):
            raise forms.ValidationError('Agents can only set In Progress or Resolved.')
        return status


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'internal']
        widgets = {'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'})}

    def __init__(self, *args, can_make_internal=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not can_make_internal:
            self.fields.pop('internal')


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
