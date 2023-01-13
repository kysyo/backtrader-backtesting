from config.influxdb_config import influxdb_client
from config.influxdb_config import measurement_name

class InfluxdbData:
    def __init__(self, start, end):
        self.influxdb_client = influxdb_client
        self.start = start
        self.end = end

    def get_influxdb_data(self):
        sql = "SELECT * " \
              "FROM {0} " \
              "WHERE TIME >= '{1}' AND TIME <= '{2}'" \
            .format(measurement_name, self.start, self.end)

        df = self.influxdb_client.query(sql)
        result_df = df[measurement_name]
        return result_df
