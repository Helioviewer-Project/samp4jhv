# Send JHV a request file

import argparse
from astropy.samp import SAMPIntegratedClient
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i", "--input", required=True, metavar="file", help="input JHV request file"
)
parser.add_argument("-value", help="Send request as message value", action="store_true")
args = parser.parse_args()

input_file = os.path.abspath(args.input)

client = SAMPIntegratedClient()
client.connect()

params = {}

if args.value:
    with open(input_file, "r") as f:
        params["value"] = f.read()
else:
    params["url"] = input_file

message = {}
message["samp.mtype"] = "jhv.load.request"
message["samp.params"] = params

client.notify_all(message)

client.disconnect()
