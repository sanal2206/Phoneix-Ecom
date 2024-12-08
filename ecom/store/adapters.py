from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Activate user for social accounts
        if not user.is_active:
            user.is_active = True
            user.verification_method = sociallogin.account.provider.capitalize()
            user.save()
        return user
