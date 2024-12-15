 # store_manager/forms.py
from django import forms
from store.models import Product, ProductImage,Variant,Storage,Colour,Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'brand', 'category', 'description', 'thumbnail', 'stock', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

            
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']

# For multiple images
ProductImageFormSet = forms.modelformset_factory(
    ProductImage,
    form=ProductImageForm,
    extra=3,  # Minimum 3 images
     
)

class ColourForm(forms.ModelForm):
    class Meta:
        model=Colour
        fields=['colour']

class StorageForm(forms.ModelForm):
    class Meta:
        model=Storage
        fields=['capacity','is_active']


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = ['product', 'colour', 'storage', 'price', 'stock', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'colour': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select colour'}),  # Using Select widget
            'storage': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select storage'}),  # Using Select widget for storage
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock quantity'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price


    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active storage options
        self.fields['storage'].queryset = Storage.objects.filter(is_active=True)
        self.fields['storage'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Select storage',
        })
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=['name','is_active']
        widget={
                
            'name': forms.TextInput(attrs={'class': 'form-control'}),
    
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }