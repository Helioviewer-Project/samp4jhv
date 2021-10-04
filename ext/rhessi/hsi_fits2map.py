from sunpy.io.fits import read
from sunpy.time import parse_time
from sunpy.map import Map


__all__ = ["hsi_fits2map"]


""" NOTE: as of february 2021 this functionality is part of sunkit-instruments v0.2 as imagecube2map()"""
def hsi_fits2map(url):
    """
    Extracts single map images from a RHESSI flare image datacube. Currently
    assumes input to be 4D.
    This function is analogous to the `hsi_fits2map.pro` functionality available in SSW.
    Parameters
    ----------
    rhessi_imagecube_file : `str`
        Path or URL to image datacube .fits
    Returns
    -------
    `dict` of `sunpy.map.MapSequence`
        Each energy band has a list of maps where the index of the lists represent the time step
    """
    f = read(url)
    header = f[0].header
    
    # remove those (non-standard) headers to avoid user warnings (they are 0 anyway)
    del header["CROTACN1"]
    del header["CROTACN2"]
    del header["CROTA"]

    d_min = {}
    d_max = {}
    for e in range(len(f[1].data[0]["ENERGY_AXIS"])):
        d_min[e] = 1e10
        d_max[e] = -1e10
        for t in range(len(f[1].data[0]["TIME_AXIS"])):
            d_min[e] = min(d_min[e], f[0].data[t][e].min())
            d_max[e] = max(d_max[e], f[0].data[t][e].max())

    maps = {}  # result dictionary
    for e in range(len(f[1].data[0]["ENERGY_AXIS"])):
        header["ENERGY_L"] = f[1].data[0]["ENERGY_AXIS"][e][0]
        header["ENERGY_H"] = f[1].data[0]["ENERGY_AXIS"][e][1]
        header["DATAMIN"] = d_min[e]
        header["DATAMAX"] = d_max[e]
        key = f"{int(header['ENERGY_L'])}-{int(header['ENERGY_H'])} keV"
        maps[key] = []
        for t in range(len(f[1].data[0]["TIME_AXIS"])):
            header["DATE_OBS"] = parse_time(f[1].data[0]["TIME_AXIS"][t][0], format='utime').to_value('isot')
            header["DATE_END"] = parse_time(f[1].data[0]["TIME_AXIS"][t][1], format='utime').to_value('isot')
            maps[key].append(Map(f[0].data[t][e], header))  # extract image into sunpy.Map
    return maps
