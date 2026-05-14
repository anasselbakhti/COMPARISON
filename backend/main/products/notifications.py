from django.core.mail import send_mail
from django.conf import settings

def envoyer_alerte_email(utilisateur, sujet, message):
    if not utilisateur.email:
        return False
    send_mail(
        sujet,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [utilisateur.email],
        fail_silently=False,
    )
    return True
