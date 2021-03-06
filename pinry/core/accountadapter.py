from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import setup_user_email
from django.conf import settings
from invitation.models import InvitationKey
from invitation.forms import InvitationKeyForm
from invitation.backends import InvitationBackend
from django.contrib.auth.models import Group 
from allauth.account.signals import user_signed_up
from django.dispatch import receiver 

is_key_valid = InvitationKey.objects.is_key_valid

class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        invitation_key = request.session.get('invitation_key', False)
        invitation_email = request.session.get('invitation_email', False)
        if getattr(settings, 'ALLOW_NEW_REGISTRATIONS', False):
            if getattr(settings, 'INVITE_MODE', False):
                if invitation_key:
                    if is_key_valid(invitation_key):
                        self.stash_email_verified(request, invitation_email)
                        return True
                    else:
                        template_name = 'invitation/wrong_invitation_key.html'
                        raise ImmediateHttpResponse(direct_to_template(request, template_name, extra_context)) 
            else:
                return True
        else:
            return False

    @receiver (user_signed_up)
    def complete_signup(sender, **kwargs):
        user = kwargs.pop('user')
        request = kwargs.pop('request')
        sociallogin = request.session.get('socialaccount_sociallogin', None)

        user.groups.add(Group.objects.get(name=settings.DEFAULT_USER_GROUP))
        user.save()
        print(user.username, ": has signed up!")
        

class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        print '----custom---------pre_social_login---------------------'
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse
        
        Why both an adapter hook and the signal? Intervening in
        e.g. the flow from within a signal handler is bad -- multiple
        handlers may be active and are executed in undetermined order.
        """
        # add sociallogin to session, because sometimes it's not there...
        request.session['socialaccount_sociallogin'] = sociallogin

