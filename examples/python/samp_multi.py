# Send JHV a series of images to load in a layer

from astropy.samp import SAMPIntegratedClient

image_list = [
    "https://api.helioviewer.org/v2/getJP2Image/?date=2019-01-01T00:00:00Z&sourceId=10",
    "https://api.helioviewer.org/v2/getJP2Image/?date=2019-01-02T00:00:00Z&sourceId=10",
    "https://api.helioviewer.org/v2/getJP2Image/?date=2019-01-03T00:00:00Z&sourceId=10",
    "https://api.helioviewer.org/v2/getJP2Image/?date=2019-01-04T00:00:00Z&sourceId=10",
    "https://api.helioviewer.org/v2/getJP2Image/?date=2019-01-05T00:00:00Z&sourceId=10",
]

client = SAMPIntegratedClient()
client.connect()

params = {}
params["url"] = image_list

message = {}
message["samp.mtype"] = "jhv.load.image"
message["samp.params"] = params

client.notify_all(message)

client.disconnect()
