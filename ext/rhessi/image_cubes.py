from requests import get as get_request
from bs4 import BeautifulSoup
import warnings


__all__ = ["IC_ALGO", "get_image_cube_url", "get_img_preview_url"]


IC_ALGO = {
    "bproj_image": "BACK_PROJECTION",
    "clean": "CLEAN",
    "clean59": "CLEAN_59",
    "ge": "MEM_GE",
    "vis_cs": "VIS_CS",
    "vf": "VIS_FWDFIT",
}


def _matching_chars(s1, s2):
    m_len = min(len(s1), len(s2))
    if m_len < 18:
        return 0

    mc = 0
    scores = [2] * m_len
    scores[11], scores[12], scores[16], scores[17] = 1, 1, 1, 1  # minutes give less score
    for i in range(m_len):
        mc += scores[i] if s1[i] == s2[i] else 0
    return mc


def _get_best_matching_subfolder(url, expected_folder, filter_func=lambda x: True):
    f = get_request(url)
    soup = BeautifulSoup(f.text, 'html.parser')

    best_match = ''
    best_score = 0
    for a in soup.find_all('a'):
        folder = a.get("href")
        if not filter_func(folder):
            continue

        score = _matching_chars(folder, expected_folder)
        if score > best_score:
            best_match = folder
            best_score = score
    return best_match


def get_image_cube_url(flare, algo="clean", base_url="https://hesperia.gsfc.nasa.gov/rhessi_extras/imagecube_fits"):
    """ get respective file from gsfc archive

    :param flare: flare object, e.g. df.iloc[0]
    :param algo: reconstruction algorithm. one of ALGO_FILENAMES
    :param base_url: base url for image cube archive
    :return: url
    """
    y = flare["START_TIME"].strftime("%Y")
    m = flare["START_TIME"].strftime("%m")
    d = flare["START_TIME"].strftime("%d")
    start = flare["START_TIME"].strftime("%H%M")
    start2 = int(start) + (1 if int(flare["START_TIME"].strftime("%S")) >= 30 else 0)
    end = flare["END_TIME"].strftime("%H%M")
    file_prefix = f"hsi_imagecube_{algo}_{y}{m}{d}_{start2}_"

    url = f"{base_url}/{y}/{m}/{d}/"
    url += _get_best_matching_subfolder(url, f"{y}{m}{d}_{start}_{end}")
    url += _get_best_matching_subfolder(url, file_prefix, lambda x: x.endswith(".fits"))

    if not url.endswith(".fits"):
        warnings.warn(f"no image cube fits file found for this flare. Check: {url}")
        return ""
    return url


def get_img_preview_url(fits_url, algo="clean", file_prefix="hsi_image_panels_scaled_"):
    base = fits_url.rsplit("/", 1)[0].replace("/imagecube_fits/", "/flare_images/") + "/" + IC_ALGO[algo] + "/"
    url = base + _get_best_matching_subfolder(base, file_prefix, lambda x: x.endswith(".jpeg"))
    
    if not url.endswith(".jpeg"):
        warnings.warn(f"no image preview found for this flare. Check: {url}")
        return ""
    return url
