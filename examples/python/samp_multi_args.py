# Send JHV a series of images to load in a layer

import argparse
from astropy.samp import SAMPIntegratedClient

parser = argparse.ArgumentParser()
parser.add_argument("-i", nargs="+")
args = parser.parse_args()

client = SAMPIntegratedClient()
client.connect()

params = {}
params["url"] = args.i

message = {}
message["samp.mtype"] = "jhv.load.image"
message["samp.params"] = params

client.notify_all(message)

client.disconnect()
