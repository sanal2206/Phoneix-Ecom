 # store_manager/forms.py
from django import forms
from store.models import Product, ProductImage,Variant,Storage,Colour,Category,Brand,Coupon,TypeCategory
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import datetime


class TypeCategoryForm(forms.ModelForm):
    class Meta:
        model=TypeCategory
        fields=['name']
        widget={
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'brand', 'category', 'type_category', 'description', 'thumbnail', 'is_active','is_featured', 'discount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            # 'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'type_category': forms.Select(attrs={'class': 'form-control'}),   
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Checkbox for featured
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount percentage'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


    brand=forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        empty_label='Select brand',
        widget=forms.Select(attrs={'class':'form-control'}),
        required=True
    )
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

 
    def clean_price(self):
        price=self.cleaned_data.get('price')
        if price is not None and price<=0:
            raise forms.ValidationError("Price must be greater than 0")
        return price


    # def clean_thumbnail(self):

    #     thumbnail=self.cleaned_data.get('thumbnail')
    #     if thumbnail:

    #         try:
    #             image=get_image_dimensions(self)
    #             if not image:
    #                 raise ValidationError("This is not a valid image.")
    #         except Exception as e:
    #             raise ValidationError("Invalid image format.")
    #     return thumbnail        
            
            

 
 
 

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percent', 'start_date', 'end_date', 'usage_limit']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon code'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount percentage'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date','min':datetime.now().isoformat()}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date','min':datetime.now().isoformat()}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter usage limit'}),
        }

    def clean_code(self):
        """
        Validate that the coupon code is unique and alphanumeric.
        """
        code = self.cleaned_data['code'].upper()  # Convert to uppercase for consistency
        if not code.isalnum():
            raise forms.ValidationError("Coupon code can only contain alphanumeric characters.")
        if Coupon.objects.filter(code=code).exists():
            raise forms.ValidationError("A coupon with this code already exists.")
        return code

    def clean_discount_percent(self):
        """
        Validate that the discount percentage is between 0 and 100.
        """
        discount_percent = self.cleaned_data['discount_percent']
        if discount_percent < 0 or discount_percent > 100:
            raise forms.ValidationError("Discount percent must be between 0 and 100.")
        return discount_percent

    from datetime import datetime

 

    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Convert current datetime to date
        today = datetime.now().date()

        if start_date and end_date:
            # Ensure both start_date and end_date are datetime.date objects
            if isinstance(start_date, datetime):
                start_date = start_date.date()
            if isinstance(end_date, datetime):
                end_date = end_date.date()

            # Compare with today's date
            if start_date < today:
                raise forms.ValidationError("The start date cannot be in the past.")
            if end_date < start_date:
                raise forms.ValidationError("The end date cannot be earlier than the start date.")

        return cleaned_data

    def clean_usage_limit(self):
        """
        Validate that the usage limit is a positive integer.
        """
        usage_limit = self.cleaned_data['usage_limit']
        if usage_limit <= 0:
            raise forms.ValidationError("Usage limit must be a positive number.")
        return usage_limit
 
    
class ColourForm(forms.ModelForm):
    class Meta:
        model=Colour
        fields=['colour']

class StorageForm(forms.ModelForm):
    class Meta:
        model=Storage
        fields=['capacity','is_active']


class BrandForm(forms.ModelForm):
    class Meta:
        model=Brand
        fields=['name']    

            
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

class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = ['product', 'colour', 'storage', 'price', 'stock','is_active']
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