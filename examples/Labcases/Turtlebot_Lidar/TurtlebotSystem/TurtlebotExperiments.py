import redis
import time
import json
import yaml
from pycaret.anomaly import *
from vfworks.utils.auxiliary import *

class TurtlebotSystem:
    def __init__(self,name,VERBOSE=True, DEPLOYED=False, monitorPeriod=0.5):
        self.model = None
        self.models = []
        self.ANOMALYDETECTORLOADED = False
        self.monitorActive = False
        self.timeStamps = []
        self.timestamp = 0.0
        self.name = name
        self.measurement = None
        self.VERBOSE = VERBOSE
        self.config = self.load_config("config.yaml")
        config = self.config['dp_config']
        self.redis_client = redis.StrictRedis(
            host=config['redis_host'],
            port=config['redis_port'],
            charset="utf-8",
            decode_responses=True,
            db=config.get('redis_db', 0)
        )

        self.monitorPeriod = monitorPeriod
        self.t_monitor = perpetualTimer(self.monitorPeriod, self.monitor)

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def collect_from_pubsub(self, duration):
        if self.ANOMALYDETECTORLOADED:
            self.monitorActive = True
            if not self.t_monitor.isAlive():
                self.t_monitor.start()
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("/Scan")

        collected_data = []
        start_time = time.time()
        try:
            for message in pubsub.listen():
                # Stop after duration
                if time.time() - start_time > duration:
                    break

                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                    except Exception:
                        data = message["data"]  # fallback if not JSON

                    collected_data.append(data)
                    if self.ANOMALYDETECTORLOADED:
                        self.measurement = data["ranges"]
        finally:
            # Clean up
            pubsub.unsubscribe("/scan")
            pubsub.close()
            self.monitorActive = False

        return collected_data

    def perform_experiment(self, duration):
        measurements = self.collect_from_pubsub(duration)
        return measurements

    def monitor(self):
        if self.monitorActive:
            # timestamps
            self.timestamp = self.timestamp + self.monitorPeriod

            #-------- PERFORM ANOMALY DETECTION-------------
            if self.ANOMALYDETECTORLOADED:
                self.anomalyDetection(self)

    # ----------------------ANOMALY DETECTION----------------------
    def anomalyDetection(self):
        print("Warning: anomaly detection function not implemented")

    def loadAnomalyDetectionModel(self, model,type="pycaret"):
        if type == "pycaret":
            self.model = load_model(model)
            self.ANOMALYDETECTORLOADED = True
        elif type == "torch":
            self.model = model
            self.models.append(model)
            self.ANOMALYDETECTORLOADED = True
        else:
            self.model = None
            self.ANOMALYDETECTORLOADED = False
