from .models import ContactMessage

def patient_messages(request):
    if request.user.is_authenticated and request.user.role == 'patient':
        messages_list = ContactMessage.objects.filter(email=request.user.email).order_by('-created_at')
        for msg in messages_list:
            msg.all_msgs = sorted(list(msg.replies.all()) + [msg], key=lambda x: x.created_at)
        return {'messages_list': messages_list}
    return {}
