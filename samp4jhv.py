from os import unlink as del_file
from tempfile import NamedTemporaryFile
from astropy.samp import SAMPIntegratedClient


__all__ = ["SAMP4JHVClient"]


class SAMP4JHVClient:
    def __init__(self):
        self.client = SAMPIntegratedClient()
        self.tmp_files = []

    def send_image_maps(self, maps):
        """ Takes a list of SunPy Map objects, saves them to disk one by one and sends the file-locations to JHV """
        
        params = {}
        params["url"] = []
        for m in maps:
            f = NamedTemporaryFile(delete=False, suffix=".fits")
            f.close()
            m.save(f.name)
            self.tmp_files.append(f.name)
            # use file:/// workaround for windows as JHV currently can't handle windows paths
            params["url"].append(("file:///" + f.name.replace("\\", "/")) if f.name.find("\\") >= 0 else f.name)

        self.client.connect()
        self.client.notify_all({"samp.mtype": "jhv.load.image", "samp.params": params})
        self.client.disconnect()

    def remove_tmp_files(self):
        """ Removes temporary files that were created for JHV to be read.
        Mind that after calling this function, the images might not be available in JHV anymore
        due to JHVs internal memory management, that might require to re-read the files at some point.
        """
        
        for f in self.tmp_files:
            del_file(f)  # cleanup

