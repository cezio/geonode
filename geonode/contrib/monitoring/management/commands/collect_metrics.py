# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from __future__ import print_function
import logging
import argparse
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_noop as _

from geonode.utils import parse_datetime
from geonode.contrib.monitoring.models import Service
from geonode.contrib.monitoring.service_handlers import get_for_service
from geonode.contrib.monitoring.collector import CollectorAPI
from geonode.contrib.monitoring.utils import TypeChecks

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Run collecting for monitoring
    """

    def add_arguments(self, parser):
        parser.add_argument('-l', '--list', dest='list_services', action='store_true', default=False,
                            help=_("Show list of services"))
        parser.add_argument('-s', '--since', dest='since', default=None, type=parse_datetime,
                            help=_("Process data since specific timestamp (YYYY-MM-DD HH:MM:SS format). If not provided, last sync will be used."))
        parser.add_argument('-u', '--until', dest='until', default=None, type=parse_datetime,
                            help=_("Process data until specific timestamp (YYYY-MM-DD HH:MM:SS format). If not provided, now will be used."))
        parser.add_argument('-f', '--force', dest='force_check', action='store_true', default=False,
                            help=_("Force check"))
        parser.add_argument('-t', '--format', default=TypeChecks.AUDIT_TYPE_JSON, type=TypeChecks.audit_format,
                            help=_("Format of audit log (xml, json)"))

        parser.add_argument('-c', '--clear', default=False, action='store_true', dest='clear',
                            help=_("Should data be cleared (default: no)"))

        parser.add_argument('service', type=TypeChecks.service_type, nargs="?",
                            help=_("Collect data from this service only"))

    def handle(self, *args, **options):
        oservice = options['service']
        if not oservice:
            services = Service.objects.all()
        else:
            services = [oservice]
        if options['list_services']:
            print('available services')
            for s in services:
                print('  ', s.name, '(', s.url, ')')
                print('   running on', s.host.name, s.host.ip)
                print('   active:', s.active)
                if s.last_check:
                    print('    last check:', s.last_check)
                else:
                    print('    not checked yet')
                print(' ')
            return
        c = CollectorAPI()
        for s in services:
            try:
                self.run_check(s, collector=c,
                                  since=options['since'], 
                                  until=options['until'],
                                  force_check=options['force_check'],
                                  format=options['format'])
            except Exception, err:
                log.error("Cannot collect from %s: %s", s, err, exc_info=err)
        if options['clear']:
            c.clear_old_data()

    def run_check(self, service, collector, since=None, until=None, force_check=None, format=None):
        print('checking', service.name, 'since', since, 'until', until )
        Handler = get_for_service(service.service_type.name)

        last_check = service.last_check
        now = datetime.now()
        since = since or last_check or now - service.check_interval
        until = until or now
        
        h = Handler(service, force_check=force_check)
        data_in = h.collect(since=since, until=until, format=format)
        if data_in:
            return collector.process(service, data_in, since, until)