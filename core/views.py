from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from .models import RfidCard, EntryLog
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_TOPIC_COMMANDS = "reader/commands"

@staff_member_required
def send_mqtt(command):
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, 1883, 60)
        client.publish(MQTT_TOPIC_COMMANDS, command)
        client.disconnect()
    except Exception:
        pass

@staff_member_required
def home(request):
    return render(request, 'home.html')

@staff_member_required
def api_latest_log(request):
    last_log = EntryLog.objects.order_by('-timestamp').first()
    if last_log:
        return JsonResponse({
            'status': last_log.status,
            'user': last_log.card.user.full_name if (last_log.card and last_log.card.user) else "Nieznany",
            'timestamp': last_log.timestamp.isoformat()
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
    send_mqtt("START_REGISTRATION_MODE")
    return redirect('card_list') 

@staff_member_required
def extend_validity(request, card_id):
    karta = get_object_or_404(RfidCard, id=card_id)
    if karta.expiry_date < timezone.now():
        karta.expiry_date = timezone.now() + timezone.timedelta(days=30)
    else:
        karta.expiry_date += timezone.timedelta(days=30)
    karta.save()
    return redirect('card_list')

@staff_member_required
def block_card(request, card_id):
    karta = get_object_or_404(RfidCard, id=card_id)
    karta.valid = not karta.valid
    karta.save()
    return redirect('card_list')

@staff_member_required
def logout_worker(request):
    logout(request)
    return redirect('/admin/login/')