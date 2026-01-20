from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from .models import RfidCard, EntryLog, CardHolder
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "localhost"
MQTT_TOPIC_COMMANDS = "reader/commands"
MQTT_TOPIC_MODE = "reader/mode"

def send_mqtt(command):
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, 1883, 60)
        client.publish(MQTT_TOPIC_MODE, command)
        client.disconnect()
    except Exception:
        pass

@staff_member_required
def home(request):
    mode = request.session.get('current_mode', 'validation')
    return render(request, 'home.html', {'current_mode': mode})

@staff_member_required
def api_latest_log(request):
    mode = request.session.get('current_mode', 'validation')
    registration_statuses = ['REGISTERED', 'UPDATED']

    if mode == 'registration':
        last_log = EntryLog.objects.filter(status__in=registration_statuses).order_by('-timestamp').first()
    else:
        last_log = EntryLog.objects.exclude(status__in=registration_statuses).order_by('-timestamp').first()

    if last_log:
        return JsonResponse({
            'status': last_log.status,
            'user': last_log.card.user.full_name if (last_log.card and last_log.card.user) else "Nieznany",
            'timestamp': last_log.timestamp.isoformat(),
            'mode': mode,
            'uid': last_log.uid_raw
        })
    return JsonResponse({})

@staff_member_required
def card_list(request):
    cards = RfidCard.objects.select_related('user').all().order_by('-expiry_date')
    return render(request, 'cards.html', {'cards': cards})

@staff_member_required
def log_list(request):
    logs = EntryLog.objects.select_related('card__user').order_by('-timestamp')[:25]
    return render(request, 'logs.html', {'logs': logs})

@staff_member_required
def start_register(request):
    msg = json.dumps({"mode": "REGISTRATION"})
    send_mqtt(msg)
    return redirect('card_list') 

@staff_member_required
def extend_validity(request, card_id):
    card = get_object_or_404(RfidCard, id=card_id)
    if card.expiry_date < timezone.now():
        card.expiry_date = timezone.now() + timezone.timedelta(days=30)
    else:
        card.expiry_date += timezone.timedelta(days=30)
    card.save()
    return redirect('card_list')

@staff_member_required
def block_card(request, card_id):
    card = get_object_or_404(RfidCard, id=card_id)
    card.valid = not card.valid
    card.save()
    return redirect('card_list')

@staff_member_required
def add_user(request, card_id):
    card = get_object_or_404(RfidCard, id=card_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')

        if card.user:
            user = card.user
            user.full_name = full_name
            user.save()
        else:
            new_holder = CardHolder.objects.create(uid=card.uid, full_name=full_name)
            card.user = new_holder

        card.save()
    return redirect('card_list')

@staff_member_required
def logout_worker(request):
    logout(request)
    return redirect('/admin/login/')

@staff_member_required
def change_mode(request, mode):
    if mode == "registration":
        payload = json.dumps({"mode": "REGISTRATION"})
    else:
        payload = json.dumps({"mode": "VALIDATION"})
    
    request.session['current_mode'] = mode

    send_mqtt(payload)

    return redirect('home')