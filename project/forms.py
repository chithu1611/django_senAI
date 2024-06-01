# from django import forms

# class MyForm(forms.Form):
#     url = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter URL'}))

from django import forms

class MyForm(forms.Form):
    text = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={'class': 'form-control'}),label=False)
