from django.http import JsonResponse, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from .models import Signal
import collections
from statistics import mean, stdev
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

def norm(request, signal_id):
    try:
        signals =  _get_signals(signal_id)
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
    except Exception as err:
        return HttpResponseServerError("Error while requesting signal_id=%s, error=%s" % (signal_id, err))

def zscore(request, signal_id):
    try:
        signals = _get_signals(signal_id)
        window = request.GET.get('window', 'MISSING')
        if window == 'MISSING':
            raise Exception('Missing window parameter')

        window = int(window)
        signals.sort(key=lambda x: x.get_date())
        back = len(signals) - 1
        front = back - 29
        zscores = []

        while front >= 0:
            signal_values = [signal.get_value() for signal in signals[front:back + 1]]
            zscore = (signals[back].get_value() - mean(signal_values)) / stdev(signal_values)
            row = {}
            row['date'] = signals[back].get_date()
            row['value'] = zscore
            zscores = [row] + zscores
            back -= 1
            front -= 1

        return JsonResponse(zscores, safe=False)
    except Exception as err:
        return HttpResponseServerError("Error while requesting signal_id=%s, error=%s" % (signal_id, err))

def _parse_coeffiecients(request):
    coeff_dict = {}
    for key, value in request.GET.lists():
        if key == 'signal':
            for signal in value:
                pieces = signal.split(',')
                if len(pieces) != 2:
                    raise Exception("Invalid request, the valid format for signal is: signal=id,weight")
                signal_id = pieces[0]
                coeff = float(pieces[1])
                coeff_dict[signal_id] = coeff

    return coeff_dict

def combine(request):
    try:
        coeff_dict = _parse_coeffiecients(request)

        data_dict = {}
        for key in coeff_dict.keys():
            data_dict[key] = _get_signals(key)

        linear_combo = collections.defaultdict(float)
        for signal_id, signals in data_dict.items():
            coeff = coeff_dict[signal_id]
            for signal in signals:
                linear_combo[signal.get_date()] += coeff * signal.get_value()

        output = []
        for date, value in linear_combo.items():
            row = {}
            row['date'] = date
            row['value'] = value
            output.append(row)

        return JsonResponse(output, safe=False)

    except Exception as err:
        return HttpResponseServerError("Error while making request=%s, error=%s" % (request.build_absolute_uri(), err))
