import time
import random

offloading_size = random.randint(100, 2000)
progress = 0
while progress < offloading_size:
    if progress > 0:
        time.sleep(1)
    progress += random.randint(100, 3000)
