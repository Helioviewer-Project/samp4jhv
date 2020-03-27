from sunpy.io.fits import read
from sunpy.time import parse_time
from sunpy.map import Map


__all__ = ["hsi_fits2map"]


def hsi_fits2map(url):
    f = read(url)
    header = f[0].header
    del header["CROTACN1"]
    del header["CROTACN2"]
    del header["CROTA"]

    d_min = 1e10
    d_max = -1e10
    for t in range(len(f[1].data[0]["TIME_AXIS"])):
        for e in range(len(f[1].data[0]["ENERGY_AXIS"])):
            d_min = min(d_min, f[0].data[t][e].min())
            d_max = max(d_max, f[0].data[t][e].max())

    maps = {}  # result dictionary
    for e in f[1].data[0]["ENERGY_AXIS"].astype('int'):
        maps[f"{e[0]}-{e[1]} keV"] = []  # init all layers (each energy band corresponds to a layer)

    header["DATAMIN"] = d_min
    header["DATAMAX"] = d_max
    for t in range(len(f[1].data[0]["TIME_AXIS"])):
        header["DATE_OBS"] = parse_time(f[1].data[0]["TIME_AXIS"][t][0], format='utime').to_value('isot')
        header["DATE_END"] = parse_time(f[1].data[0]["TIME_AXIS"][t][1], format='utime').to_value('isot')
        for e in range(len(f[1].data[0]["ENERGY_AXIS"])):
            header["ENERGY_L"] = f[1].data[0]["ENERGY_AXIS"][e][0]
            header["ENERGY_H"] = f[1].data[0]["ENERGY_AXIS"][e][1]
            key = f"{int(header['ENERGY_L'])}-{int(header['ENERGY_H'])} keV"
            maps[key].append(Map(f[0].data[t][e], header))  # extract image into sunpy.Map
    return maps
