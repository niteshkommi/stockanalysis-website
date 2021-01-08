from .models import endOfDay
from .views import testModule

def my_scheduled_job():
    endOfDay.objects.create(symbol="TEST5")
