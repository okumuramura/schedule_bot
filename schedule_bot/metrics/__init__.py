from prometheus_client import Histogram, Counter, start_http_server

from schedule_bot import METRICS_PORT

COMMAND_LATENCY_SECONDS = Histogram('bot_command_latency_seconds', 'command latency', ['command'])
COMMAND_USED_TOTAL = Counter('bot_command_used_total', 'count of used commands', ['command'])
NEW_USERS = Counter('bot_new_users_total', 'count of new users')


def start_metrics():
    start_http_server(port=METRICS_PORT)
