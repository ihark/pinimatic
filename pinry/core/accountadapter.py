from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from invitation.models import InvitationKey
from invitation.forms import InvitationKeyForm
from invitation.backends import InvitationBackend

is_key_valid = InvitationKey.objects.is_key_valid

class AccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        invitation_key = request.session.get('invitation_key', False)
        print '--account adapter--invitation key--', invitation_key
        
        if getattr(settings, 'ALLOW_NEW_REGISTRATIONS', False):
            if getattr(settings, 'INVITE_MODE', False):
                if invitation_key:
                    if is_key_valid(invitation_key):
                        return True
                    else:
                        template_name = 'invitation/wrong_invitation_key.html'
                        raise ImmediateHttpResponse(direct_to_template(request, template_name, extra_context)) 
            else:
                return True
        else:
            return False
            
