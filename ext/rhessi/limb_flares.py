import os
from datetime import datetime
from requests import get as get_request


__all__ = ["read_limb_flares"]


DEFAULT_LIMB_FLARE_LOCATION = os.path.join(os.path.dirname(__file__), "limb_flares_combined.txt")


def read_limb_flares(flare_list=DEFAULT_LIMB_FLARE_LOCATION):
    # load data
    if os.path.isfile(flare_list):
        with open(flare_list) as tsv:
            lines = tsv.read().split("\n")
    else:
        lines = get_request(flare_list).text.split("\n")

    flares = []
    for line in lines:
        cell = line.split(
            "\t")  # 1, 2002 Mar 07, 17:50:44, C2.5, -961.5, -176.4, 21.4, 11.6, 5.86, 32.0, 10.1, 4.56, -0.4, 0.77, 12,
        if len(cell) > 2:
            flares.append(datetime.strptime(cell[1] + "T" + cell[2], "%Y %b %dT%H:%M:%S"))

    return flares
