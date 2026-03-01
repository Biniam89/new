from django import forms
from .models import Phone, Brand, Comment

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'country_of_origin']

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = [
            'title', 'brand', 'price', 
            'storage_capacity', 'ram', 'screen_size', 'battery', 
            'description', 'image', 'stock'
        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'rating', 'body'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'rating': forms.Select(attrs={'class': 'form-select'}), 
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your review...', 'rows': 3}),
        }