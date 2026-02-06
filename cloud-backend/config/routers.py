"""Database router for time-series data"""

class TimeSeriesRouter:
    """Route sensor data models to TimescaleDB"""

    TIMESERIES_MODELS = {
        'sensorreading',
        'sensoraggregates',
        'temperaturelog',
        'humiditylog',
    }

    def db_for_read(self, model, **hints):
        if model._meta.model_name in self.TIMESERIES_MODELS:
            return 'timeseries'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.model_name in self.TIMESERIES_MODELS:
            return 'timeseries'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in self.TIMESERIES_MODELS:
            return db == 'timeseries'
        return db == 'default'
