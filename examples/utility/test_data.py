
class Timeserie_testdata:

    def __init__(self, full_name, guid, timskey, start_time_ticks, start_time_json, end_time_ticks, end_time_json, database):
        self.full_name = full_name
        self.guid = guid
        self.timskey = timskey
        self.start_time_ticks = start_time_ticks
        self.start_time_json = start_time_json
        self.end_time_ticks = end_time_ticks
        self.end_time_json = end_time_json
        self.database = database

# ------------------------------------------------------------------------------

# A smaller segment
# 01.05.2016 : 635976576000000000
# 14.05.2016 : 635987808000000000

eagle_wind = Timeserie_testdata(
    "Resource/Wind Power/WindPower/WPModel/WindProdForec(0)",
    "3f1afdd7-5f7e-45f9-824f-a7adc09cff8e",
    201503,
    635103072000000000,  # 25/07/2013 00:00:00
    "2013-07-25T00:00:00Z",
    636182208000000000,  # 25/12/2016 00:00:00
    "2016-12-25T00:00:00Z",
    "eagle"
)

