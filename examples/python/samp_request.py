# Send JHV a request file

import argparse
from astropy.samp import SAMPIntegratedClient
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i", "--input", required=True, metavar="file", help="input JHV request file"
)
args = parser.parse_args()

client = SAMPIntegratedClient()
client.connect()

params = {}
params["url"] = os.path.abspath(args.input)

message = {}
message["samp.mtype"] = "jhv.load.request"
message["samp.params"] = params

client.notify_all(message)

client.disconnect()
