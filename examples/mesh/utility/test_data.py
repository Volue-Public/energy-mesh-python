
class Timeserie_testdata:

    def __init__(self, full_name, guid, timskey, start_time, end_time, database):
        self.full_name = full_name
        self.guid = guid
        self.timskey = timskey
        self.start_time = start_time
        self.end_time = end_time
        self.database = database

# ------------------------------------------------------------------------------

# A smaller segment
# 01.05.2016 : 635976576000000000
# 14.05.2016 : 635987808000000000

eagle_wind = Timeserie_testdata(
    "Resource/Wind Power/WindPower/WPModel/WindProdForec(0)",
    "3f1afdd7-5f7e-45f9-824f-a7adc09cff8e",
    201503,
    635103072000000000, # 25/07/2013 00:00:00
    636182208000000000, # 25/12/2016 00:00:00
    "eagle"
)

