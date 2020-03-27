from os import unlink as del_file
import time
from tempfile import NamedTemporaryFile
from astropy.samp import SAMPIntegratedClient


__all__ = ["send_map_layers_to_samp"]


def send_map_layers_to_samp(maps, defer_cleanup_s=3):
    client = SAMPIntegratedClient()
    client.connect()
    params = {}
    message = {"samp.mtype": "jhv.load.image", "samp.params": params}

    tmp_files = []
    for energy_band in maps:
        params["url"] = []
        for i in range(len(maps[energy_band])):
            f = NamedTemporaryFile(delete=False, suffix=".fits")
            f.close()
            maps[energy_band][i].save(f.name)
            tmp_files.append(f.name)
            # use file:/// workaround for windows as JHV currently can't handle windows paths
            params["url"].append(("file:///" + f.name.replace("\\", "/")) if f.name.find("\\") >= 0 else f.name)
        client.notify_all(message)  # message holds a reference to params which is updated in the loop
    client.disconnect()

    time.sleep(defer_cleanup_s)  # wait to make sure JHV could read the files before they're removed
    for filename in tmp_files:
        del_file(filename)  # cleanup
