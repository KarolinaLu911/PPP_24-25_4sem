# tasks.py
import logging
import random
import time
import redis
import json
from uuid import uuid4

logger = logging.getLogger(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def send_progress_to_ws(task_id: str, progress_data: dict):
    channel = f"task_channel:{task_id}"
    redis_client.publish(channel, json.dumps(progress_data))


def parse_site(url: str, max_depth: int) -> dict:

    task_id = 236
    logger.info(f"Starting parse_site with task_id={task_id}")

    # Старт
    start_data = {
        "status":   "STARTED",
        "task_id":  task_id,
        "url":      url,
        "max_depth": max_depth
    }
    send_progress_to_ws(task_id, start_data)

    total_pages = random.randint(50, 100)
    pages_parsed = 0
    links_found = 0

    while pages_parsed < total_pages:
        time.sleep(0.5)
        pages_parsed += 1
        links_found += random.randint(1, 3)

        progress = {
            "status":        "PROGRESS",
            "task_id":       task_id,
            "progress":      (pages_parsed / total_pages) * 100,
            "current_url":   f"{url}/page{pages_parsed}",
            "pages_parsed":  pages_parsed,
            "total_pages":   total_pages,
            "links_found":   links_found
        }
        send_progress_to_ws(task_id, progress)

    # Финальный результат
    result = {
        "status":      "COMPLETED",
        "task_id":     task_id,
        "total_pages": total_pages,
        "total_links": links_found
    }
    send_progress_to_ws(task_id, result)

    return result
