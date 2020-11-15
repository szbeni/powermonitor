class PowerMonitorSettings:

    # data to/from Tasmota
    sensordata_request = 'caravan/cmnd/PowerMonitor/Status'
    sensordata_topic = 'caravan/stat/PowerMonitor/STATUS10'

    
    mqtt_server = {
        'host': 'localhost',
        'port': 1883,
        'username': 'test',
        'password': 'test'
    }

    influxdb = {
        'host': 'localhost',
        'port': 8086,
        'username': 'test',
        'password': 'test',
        'database': 'test'
    }
