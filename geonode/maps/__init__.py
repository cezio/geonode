# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
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
import logging
from django.apps import AppConfig
from django.utils.translation import ugettext_noop as _
from geonode.notifications_helper import install_notifications

logger = logging.getLogger(__name__)

notifications = (("map_updated", _("Map Updated"), _("A Map was updated"),),
                 ("map_deleted", _("Map Deleted"), _("A Map was deleted"),),
                 ("map_comment", _("Comment on Map"), _("A map was commented on"),),
                 ("map_rated", _("Rating for Map"), _("A rating was given to a map"),),
                )

class MapsAppConfig(AppConfig):
    name = 'geonode.maps'

    def ready(self):
        install_notifications(notifications, logger, self)

default_app_config = 'geonode.maps.MapsAppConfig'
