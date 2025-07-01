
import os
import json
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()
CONFIG = {k: v for k, v in os.environ.items() if any(s in k for s in ['_KEY', '_TOKEN', '_SERVER', '_ACCOUNT', '_PORT'])}

# Logger setup
logger = logging.getLogger("DigiManCore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Metrics
metrics = {
    "tasks_processed": 0,
    "tasks_failed": 0,
    "agents_generated": 0,
    "clients_onboarded": 0,
    "revenue_generated": 0,
    "client_satisfaction": 0,
    "leads_generated": 0
}
