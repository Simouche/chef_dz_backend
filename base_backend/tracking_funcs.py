import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def have_met(latitudes_p1, latitudes_p2, longitudes_p1, longitudes_p2):
    if len(latitudes_p1) == 0 or len(latitudes_p2) == 0 or len(longitudes_p1) == 0 or len(longitudes_p2) == 0:
        return False, 0

    next_lat = 0
    for i in latitudes_p1:
        for j in latitudes_p2:
            if abs(i - j) <= 0.00001:
                next_lat += 1

    next_long = 0
    for i in longitudes_p1:
        for j in longitudes_p2:
            if abs(i - j) <= 0.00001:
                next_long += 1

    if next_lat >= 3 and next_long >= 3:
        return True, min(next_long, next_lat)
    return False, 0


def check_users():
    import time
    time.sleep(10)
    from .models import BeenInContactWith
    from sos_app.models import User
    while True:
        users_count = User.objects.all().count()
        if users_count <= 1:
            logger.info("no user to check.")
            return
        from datetime import datetime, timedelta
        last_hour = datetime.now() - timedelta(hours=1)
        last_hour = timezone.make_aware(last_hour, timezone.get_default_timezone())
        all_users = User.objects.all()
        ids = []
        for user1 in all_users:
            ids.append(user1.id)
            latitudes_p1 = user1.userlocation_set.filter(created_at__gte=last_hour).values_list("latitude", flat=True)
            longitudes_p1 = user1.userlocation_set.filter(created_at__gte=last_hour).values_list("longitude", flat=True)
            for user2 in all_users:
                if user2.id in ids:
                    continue

                latitudes_p2 = user2.userlocation_set.filter(created_at__gte=last_hour) \
                    .values_list("latitude", flat=True)
                longitudes_p2 = user2.userlocation_set.filter(created_at__gte=last_hour) \
                    .values_list("longitude", flat=True)
                have_they, duration = have_met(latitudes_p1, latitudes_p2, longitudes_p1, longitudes_p2)
                if have_they:
                    BeenInContactWith.objects.create(first=user1, second=user2, duration=duration * 10)

        logger.info("finished checking meetings")
        time.sleep(3600)


def measure(latitude1, longitude1, latitude2, longitude2):
    import math
    latitude1 = float(latitude1)
    longitude1 = float(longitude1)
    r = 6378.137  # Radius of earth in KM
    d_lat = latitude2 * math.pi / 180 - latitude1 * math.pi / 180
    d_lon = (longitude2) * math.pi / 180 - longitude1 * math.pi / 180
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(latitude1 * math.pi / 180) * math.cos(
        latitude2 * math.pi / 180) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r * c
    return d * 1000  # meters
