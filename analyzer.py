# coding=utf-8
from __future__ import absolute_import
import time
import json


class SimpleAnalyzer(object):
    analytics_data = {
        'pv': 0,
        'vs': 0,
        'uv': 0,
        'ip': 0,
    }
    analytics_page_data = {}
    period = {
        'vs': [],
        'uv': [],
        'ip': [],
    }
    period_day = 0
    period_online = 0

    live_mins = 60 * 30
    live_day = 3600 * 24

    period_size_limit = 6000
    write_timer = 0
    write_cycle = 3600 * 12
    data_src = 'analytics.json'

    def __init__(self):
        self.period_day = time.time()
        self.period_online = time.time()
        self.write_timer = time.time()

        try:
            with open(self.data_src) as f:
                loaded = json.load(f)
        except Exception:
            loaded = {}

        if loaded:
            self.analytics_data = {
                "pv": loaded.get('pv') or 0,
                "vs": loaded.get('vs') or 0,
                "uv": loaded.get('uv') or 0,
                "ip": loaded.get('uv') or 0,
            }
            counted_pages = loaded.get('pages') or {}
            for k, v in counted_pages.iteritems():
                self.analytics_page_data[k] = v

    def get_app(self):
        page_view = self.analytics_data.get('pv') or 0
        visit = self.analytics_data.get('vs') or 0
        unique_visitor = self.analytics_data.get('uv') or 0
        unique_ip = self.analytics_data.get('ip') or 0
        return {
            'pv': page_view,
            'vs': visit,
            'uv': unique_visitor,
            'ip': unique_ip
        }

    def get_page(self, page_id):
        page_view = self.analytics_page_data.get(page_id) or 0
        return {
            'pv': page_view
        }

    def count_page(self, page_id):
        if page_id in self.analytics_page_data:
            self.analytics_page_data[page_id] += 1
        else:
            self.analytics_page_data[page_id] = 1

    def count_app(self, remote_addr='', user_agent=''):
        ip_user_agent = "{}.{}".format(remote_addr, user_agent)

        self.analytics_data["pv"] += 1

        if ip_user_agent not in self.period['vs']:
            self.analytics_data["vs"] += 1
        if ip_user_agent not in self.period['uv']:
            self.analytics_data["uv"] += 1
        if ip_user_agent not in self.period['ip']:
            self.analytics_data["ip"] += 1

        if time.time() - self.period_online < self.live_mins:
            self._append_period(self.period['vs'], ip_user_agent)
        else:
            self.period['vs'] = []
            self.period_online = time.time()

        if time.time() - self.period_day < self.live_day:
            self._append_period(self.period['uv'], ip_user_agent)
            self._append_period(self.period['ip'], ip_user_agent)
        else:
            self.period['uv'] = []
            self.period['ip'] = []
            self.period_day = time.time()

        self._write_data()

    def _append_period(self, period_list, text):
        period_list.append(text)
        if period_list and len(period_list) > self.period_size_limit:
            period_list.pop(0)

    def _write_data(self):
        if time.time() - self.write_timer < self.write_cycle:
            return
        self.write_timer = time.time()
        data = self.analytics_data
        data['pages'] = self.analytics_page_data
        try:
            with open(self.data_src, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print e
