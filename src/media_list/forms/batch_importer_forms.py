from django import forms


class BatchImporterInputForm(forms.Form):
    links = forms.CharField(widget=forms.Textarea)
