from requests import get as get_request
from bs4 import BeautifulSoup
import warnings
from datetime import datetime


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
    # calculates how many chars match in s1 and s2
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
    return best_match, best_score


def _get_largest_timeoverlap_subfolder(url, expected_folder, offset=9):
    # gets best matching subfolder based on differences of start- and endtimes
    # offset determines the start of a %H%M_%H%M pattern that determines start and endtime
    # default (9) is for standard pattern yyyymmdd_HHMM_HHMM
    f = get_request(url)
    soup = BeautifulSoup(f.text, 'html.parser')

    best_match = ''
    best_overlap = 0
    exp_start = datetime.strptime(expected_folder[offset:offset+4], "%H%M")
    exp_end = datetime.strptime(expected_folder[offset+5:offset+9], "%H%M")
    for a in soup.find_all('a'):
        folder = a.get("href")
        if folder[:offset] != expected_folder[:offset]:
            continue

        start_max = max(exp_start, datetime.strptime(folder[offset:offset+4], "%H%M"))
        end_min = min(exp_end, datetime.strptime(folder[offset+5:offset+9], "%H%M"))
        overlap = (end_min - start_max).total_seconds()
        if overlap > best_overlap and overlap > 0:
            best_match = folder
            best_overlap = overlap
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
    end = flare["END_TIME"].strftime("%H%M")
    file_prefix = f"hsi_imagecube_{algo}_{y}{m}{d}_{start}_"

    url = f"{base_url}/{y}/{m}/{d}/"
    match = _get_largest_timeoverlap_subfolder(url, f"{y}{m}{d}_{start}_{end}")
    if match == "":
        warnings.warn(f"no fits folder found for this flare. Check: {url}")
        return ""
    url += match

    match, score = _get_best_matching_subfolder(url, file_prefix, lambda x: x.endswith(".fits"))
    if match == "":
        warnings.warn(f"no image cube fits file found for this flare. Check: {url}")
        return ""
    if len(file_prefix) - score >= 4:
        warnings.warn(f"found image cube fits file but large difference detected: Compare: {file_prefix}:{match}")
    url += match
    return url


def get_img_preview_url(fits_url, algo="clean", file_prefix="hsi_image_panels_scaled_"):
    base = fits_url.rsplit("/", 1)[0].replace("/imagecube_fits/", "/flare_images/") + "/" + IC_ALGO[algo] + "/"
    match, score = _get_best_matching_subfolder(base, file_prefix, lambda x: x.endswith(".jpeg"))
    if not match.endswith(".jpeg"):
        print(f"no image preview found for this flare. Check: {base + match}", file=sys.stderr)
        return ""
    return base + match
