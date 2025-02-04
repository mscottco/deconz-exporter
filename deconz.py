from prometheus_client import Gauge
import json

_gauges = {
  "battery": Gauge("deconz_sensor_battery", "Battery level of sensor in percent", ["manufacturer", "model", "name"]),
  "humidity": Gauge("deconz_sensor_humidity", "Humidity of sensor in percent", ["manufacturer", "model", "name", "type", "uid"]),
  "pressure": Gauge("deconz_sensor_pressure", "Air pressure in hectopascal (hPa)", ["manufacturer", "model", "name", "type", "uid"]),
  "temperature": Gauge("deconz_sensor_temperature", "Temperature of sensor in Celsius", ["manufacturer", "model", "name", "type", "uid"]),
  "open": Gauge("deconz_sensor_contact", "Contact Sensor", ["manufacturer", "model", "name", "type", "uid"]),
  "presence": Gauge("deconz_sensor_motion", "Motion Sensor", ["manufacturer", "model", "name", "type", "uid"]),
  "lux": Gauge("deconz_sensor_lux", "Light Sensor", ["manufacturer", "model", "name", "type", "uid"]),
  "consumption": Gauge("deconz_sensor_consumption", "Consumption (kWh)", ["manufacturer", "model", "name", "type", "uid"]),
  "power": Gauge("deconz_sensor_current", "Power Current (W)", ["manufacturer", "model", "name", "type", "uid"]),
};

_functionMap = {
  'ZHAHumidity': lambda x: _extract_basic_metric(x, 'humidity', 100),
  'ZHATemperature': lambda x: _extract_basic_metric(x, 'temperature', 100),
  'ZHAPressure': lambda x: _extract_basic_metric(x, 'pressure', 1),
  'ZHAOpenClose': lambda x: _extract_basic_metric(x, 'open', 1),
  'ZHAPresence': lambda x: _extract_basic_metric(x, 'presence', 1),
  'ZHALightLevel': lambda x: _extract_basic_metric(x, 'lux', 1),
  'ZHAConsumption': lambda x: _extract_basic_metric(x, 'consumption', 1000),
  'ZHAPower': lambda x: _extract_basic_metric(x, 'power', 1),
};


def _extract_basic_metric(metric, metricName, divider):
    value = float(metric['state'][metricName])/divider;

    _gauges[metricName].labels(
      manufacturer = metric['manufacturername'],
      model=metric['modelid'],
      name=metric['name'],
      type=metric['type'],
      uid=metric['uniqueid'],
    ).set(value);

def extract_metrics(logger, request_content):
  data = json.loads(request_content.decode('utf-8'));
  _extract_battery(data);

  for key in data:
    metric = data[key];

    if metric['type'] in _functionMap:
      _functionMap[metric['type']](metric);
    else:
      logger.info(f"Unknown metric type \"{metric['type']}\".");

def _extract_battery(data):
  processed = set();

  for key in data:
    value = 0;
    metric = data[key];

    if metric['name'] in processed:
      continue;

    processed.add(metric['name']);
    config = metric['config'];

    if 'battery' in config:
      value = int(config['battery']);

    _gauges['battery'].labels(manufacturer = metric['manufacturername'], model=metric['modelid'], name=metric['name']).set(value);
