# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import Review,Address
from image_cropping import ImageCropWidget
import re


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

	class Meta:
		model = get_user_model()
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
		
 

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'rating']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your review',
                'rows': 6,
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-inline rating-options'
            }, choices=[
                (1, '1'),
                (2, '2'),
                (3, '3'),
                (4, '4'),
                (5, '5'),
            ]),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5")
        return rating
    

COUNTRIES = [
        ('IN', 'India'),
        ('US', 'United States'),
        ('GB', 'United Kingdom'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('MX', 'Mexico'),
        ('BR', 'Brazil'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('RU', 'Russia'),
        ('ZA', 'South Africa'),
        ('SG', 'Singapore'),
        ('KR', 'South Korea'),
        ('IN', 'India'),
        ('NG', 'Nigeria'),
        ('AE', 'United Arab Emirates'),
    ]


class AddressForm(forms.ModelForm):
  
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country']
        
        widgets = {
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address line 1'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address line 2 (optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your state'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your postal code'}),
            'country': forms.Select(choices=COUNTRIES, attrs={'class': 'form-select', 'placeholder': 'Select your country'}),
        }

    # Custom validation method to apply to all address-related fields
    def validate_address_field(self, field_value, field_name):
        if not field_value.strip():
            raise forms.ValidationError(f"{field_name} cannot be empty.")
        
        # Allow alphanumeric characters, spaces, commas, periods, hyphens, and slashes
        if not re.match(r'^[a-zA-Z0-9\s,.-/]*$', field_value):
            raise forms.ValidationError(f"{field_name} can only contain letters, numbers, spaces, commas, periods, hyphens, and slashes.")

    def clean_address_line_1(self):
        address_line_1 = self.cleaned_data.get('address_line_1')
        self.validate_address_field(address_line_1, "Address line 1")  # Apply custom validation
        return address_line_1

    def clean_address_line_2(self):
        address_line_2 = self.cleaned_data.get('address_line_2')
        self.validate_address_field(address_line_2, "Address line 2")  # Apply custom validation
        return address_line_2

    def clean_city(self):
        city = self.cleaned_data.get('city')
        self.validate_address_field(city, "City")  # Apply custom validation
        return city

    def clean_state(self):
        state = self.cleaned_data.get('state')
        self.validate_address_field(state, "State")  # Apply custom validation
        return state

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')

        # Postal code validation regex
        if not re.match(r'^\d{5,10}$', postal_code):
            raise forms.ValidationError("Invalid postal code format. It should be a 5-10 digit number.")
        
        return postal_code

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country:
            raise forms.ValidationError("Country cannot be empty.")
        self.validate_address_field(country, "Country")  # Apply custom validation
        return country



User = get_user_model()
class UserProfileForm(forms.ModelForm):
    class Meta:
        model =User 
        fields = ['profile_photo','first_name', 'last_name', 'email','username','phone_number']
        widgets = {
            'profile_photo': ImageCropWidget(),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

class ReturnRequestForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Explain the reason for the return'}),
        label="Reason for Return",
        required=True
    )