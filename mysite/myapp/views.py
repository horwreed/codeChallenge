from django.http import JsonResponse, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from .models import Signal
import json
import requests
import sys

def _get_signals(signal_id):
    request_str = 'http://predata-challenge.herokuapp.com/signals/%s' % signal_id
    r = requests.get(request_str)
    r.raise_for_status()
    r_json = r.json()

    signals = []
    for line in r_json:
        date = line['date']
        value = line['value']
        signals.append(Signal(date, value))

    return signals

def normalize(request, signal_id):
    signals = []
    try:
        signals =  _get_signals(signal_id)
    except Exception as err:
        return HttpResponseServerError("Error while requesting signal_id=%s, error=%s" % (signal_id, err))

    normalized_signals = []
    signal_max = max(signal.get_value() for signal in signals)
    signal_min = min(signal.get_value() for signal in signals)

    for signal in signals:
        normalized_signal = (signal.get_value() - signal_min) / (signal_max - signal_min) * 100
        row = {}
        row['date'] = signal.get_date()
        row['value'] = normalized_signal
        normalized_signals.append(row)

    return JsonResponse(normalized_signals, safe=False)