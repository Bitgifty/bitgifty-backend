from django.db import models

# Create your models here.


class Point(models.Model):
    wallet_address = models.CharField(max_length=255, db_index=True)
    point = models.FloatField(default=0.0)

    def __str__(self):
        return self.wallet_address


def save_point(address: str, points):
    # First try to get existing points
    existing_points = Point.objects.filter(
        wallet_address=address
    ).values_list('point', flat=True).first()

    # Calculate the new points value
    new_points = points if existing_points is None else existing_points + points

    point_obj, created = Point.objects.update_or_create(
        wallet_address=address,
        defaults={'point': new_points}
    )

    return point_obj
