import warnings
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.error import HTTPError
from collections.abc import Iterable

import sunpy.io.fits
from sunpy.time import parse_time


__all__ = [
    "get_flare_list", "read_flare_list_file", "print_flare_list","filter_flares_by_time", "KNOWN_FLARE_LIST_SOURCES"
]


KNOWN_FLARE_LIST_SOURCES = {
    "NASA": "https://hesperia.gsfc.nasa.gov/hessidata/dbase/",
    "Berkeley": "http://hessi.ssl.berkeley.edu/hessidata/dbase/",
    "i4DS": "http://soleil.i4ds.ch/hessidata/dbase/",
}

# dictionary to map raw flagIDs provided by fits to a more readable string indicating
# presence/absence of the flags - in the same way as in the available .txt flare lists.
FLAGID2FLAG = {
    'SAA_AT_START': 'SS',
    'SAA_AT_END': 'SE',
    'SAA_DURING_FLARE': 'SD',
    'ECLIPSE_AT_START': 'ES',
    'ECLIPSE_AT_END': 'EE',
    'ECLIPSE_DURING_FLARE': 'ED',
    'FLARE_AT_SOF': 'FS',
    'FLARE_AT_EOF': 'FE',
    'NON_SOLAR': 'NS',
    'FAST_RATE_MODE': 'FR',
    'FRONT_DECIMATION': 'DF',
    'ATT_STATE_AT_PEAK': '',  # 0-3 -> changes flag an to An
    'DATA_GAP_AT_START': 'GS',
    'DATA_GAP_AT_END': 'GE',
    'DATA_GAP_DURING_FLARE': 'GD',
    'PARTICLE_EVENT': 'PE',
    'DATA_QUALITY': 'Qn',  # 0-11
    'POSITION_QUALITY': 'P1',
    'ATTEN_0': 'a0',
    'ATTEN_1': 'a1',
    'ATTEN_2': 'a2',
    'ATTEN_3': 'a3',
    'REAR_DECIMATION': 'DR',
    'MAGNETIC_REGION': 'MR',
    'IMAGE_STATUS': '',
    'SPECTRUM_STATUS': '',
    'SOLAR_UNCONFIRMED': 'PS',
    'SOLAR': ''
}


def get_flare_list(start, end, source='NASA', file_format="hessi_flare_list_%Y%m.fits", inc=relativedelta(months=+1)):
    """
    Read and combine RHESSI flare lists from .fits files as specified with further parameters
    Dates are allowed in the following formats:
        'YY-mm', 'YYYYmm', 'YYYY-mm', 'YYYYmmdd', 'YYYY-mm-dd', 'YYYY-mm-ddThh:MM:ss'

    Parameters
    ----------
    start : `str`
        Start date of period within which flares should be loaded.
    end : `str`
        End date of period within which flares should be loaded.
    source : `str`, optional
        Source from where .fits files should be loaded. Can be an URL or a local folder.
        Known sources are "NASA" and "i4DS".
        Defaults to ``"NASA"``.
    file_format : `str`, optional
        Specifies the naming convention of the files available in the source folder.
        The changing parts should be given as format string as in ``strftime``.
        Defaults to ``"hessi_flare_list_%Y%m.fits"``.
    inc : `timedelta`, `relativedelta`, optional
        Specifies by how much time the single files are separated.
        Defaults to ``relativedelta(months=+1)``.

    Returns
    -------
    ``pandas.DataFrame``
        out : ``pandas.DataFrame`` containing the flares within the given time constraints
    """

    formats = {
        5: "%y-%m",  # YY-mm
        6: "%Y%m",  # YYYYmm
        7: "%Y-%m",  # YYYY-mm
        8: "%Y%m%d",  # YYYYmmdd
        10: "%Y-%m-%d",  # YYYY-mm-dd
        19: "%Y-%m-%dT%H:%M:%S",  # YYYY-mm-ddThh:MM:ss
    }
    try:
        start_dt = datetime.strptime(start, formats[len(start)])
        end_dt = datetime.strptime(end, formats[len(end)])
    except (KeyError, ValueError):
        raise ValueError("invalid datetime")

    format_str = file_format[file_format.index("%"):file_format.rindex("%") + 2]
    cur_format = start_dt.strftime(format_str)
    end_format = end_dt.strftime(format_str)

    if source in KNOWN_FLARE_LIST_SOURCES:
        source = KNOWN_FLARE_LIST_SOURCES[source]

    cur_dt = start_dt
    result = pd.DataFrame()
    while cur_format <= end_format:
        file = file_format.replace(format_str, cur_format)
        cur_dt = cur_dt + inc
        cur_format = cur_dt.strftime(format_str)

        # allow missing files with a warning, e.g. there is no file for 2014-07
        try:
            result = result.append(read_flare_list_file(source + file), ignore_index=True)
        except HTTPError as e:
            if e.code == 404:
                warnings.warn("Skipped: " + file + " (" + str(e.code) + " " + e.msg + ")")
            else:
                raise

    # filter results for more detailed time constraints (if applicable)
    if len(end) < 8:
        end_dt += relativedelta(months=+1, microseconds=-1)  # add month -1ms to address inclusive right bound
    elif len(end) <= 10:
        end_dt += relativedelta(days=+1, microseconds=-1)  # add day if end date was specified on a day-basis

    left_bound = result['END_TIME'].searchsorted(start_dt, 'left')  # END_TIME >= start_dt
    right_bound = result['START_TIME'].searchsorted(end_dt, 'right')  # START_TIME <= end_dt  (inclusive)
    return result[left_bound:right_bound]


def read_flare_list_file(file):
    """
    Read RHESSI flare list .fits file into ``pandas.DataFrame``.
    TIME values are parsed with format 'utime', which is the same as Unix timestamp but starts 9 years later.
    FLAGS are assigned their respective label (FLAG ID) and returned as `dict`.

    Parameters
    ----------
    file : `str`
        The URL or local filename of the hessi flare list.

    Returns
    -------
    ``pandas.DataFrame``
        out : ``pandas.DataFrame`` containing the parsed flares.

    References
    ----------
    https://hesperia.gsfc.nasa.gov/rhessi3/data-access/rhessi-data/flare-list/index.html
    """
    fits = sunpy.io.fits.read(file)

    results = []
    time_offset = parse_time(0, format="utime").to_value("unix")
    for row in fits[3].data:
        result_row = {}
        for k in fits[3].data.columns.names:
            if k.endswith('_TIME'):
                if isinstance(row[k], Iterable):
                    result_row[k] = [datetime.utcfromtimestamp(t + time_offset) for t in row[k]]  # BCK_, IMAGE_
                else:
                    result_row[k] = datetime.utcfromtimestamp(row[k] + time_offset)  # START_, END_, PEAK_
            elif k == 'FLAGS':
                result_row[k] = {fid: i for (i, fid) in zip(row[k], fits[2].data['FLAG_IDS'][0])}
            else:
                result_row[k] = row[k]

        # add reformatted and calculated fields
        result_row["FLAGS_FORMATTED"] = " ".join(_convert_flag_dict(result_row['FLAGS']))
        result_row["DURATION"] = int(round((result_row['END_TIME'] - result_row['START_TIME']).total_seconds()))
        result_row["POS_RADIAL"] = int(round((result_row['POSITION'][0] ** 2 + result_row['POSITION'][1] ** 2) ** 0.5))
        results.append(result_row)

    return pd.DataFrame(results)


def print_flare_list(data_frame):
    """
    Convert and print flares similar to the available .txt flare lists.

    Parameters
    ----------
    data_frame : ``pandas.DataFrame``
        DataFrame containing the flares to print.
    """

    for idx, row in data_frame.iterrows():
        print(
            "{id:9} {st} {pt} {et} {dur:5} {peak:6} {n:9} {e:>11} {x:5} {y:5} {r:6} {ar:4}  {flags}".format(
                id=row['ID_NUMBER'],
                st=row['START_TIME'].strftime('%e-%b-%Y %H:%M:%S'),
                pt=row['PEAK_TIME'].strftime('%H:%M:%S'),
                et=row['END_TIME'].strftime('%H:%M:%S'),
                dur=row['DURATION'],
                peak=int(row['PEAK_COUNTRATE']),
                n=int(row['TOTAL_COUNTS']),
                e=str(int(row['ENERGY_HI'][0])) + "-" + str(int(row['ENERGY_HI'][1])),
                x=int(round(row['POSITION'][0])),
                y=int(round(row['POSITION'][1])),
                r=int(round(row['POS_RADIAL'])),
                ar=row['ACTIVE_REGION'],
                flags=row['FLAGS_FORMATTED'],
            )
        )


def _convert_flag_dict(flags_dict):
    """
    Convert flag dictionary into array of short abbreviations (as in available .txt lists).

    Parameters
    ----------
    flags_dict : `dict`
        Dictionary containing the flags where key is the flag id and value the value from the byte mask.

    Returns
    -------
    `list`
        out : `list` of 2-character strings, each representing a present flag (as in available .txt lists).

    """
    flags = []
    for k in flags_dict:
        # note: as of now the Q-flag is missing if the flag DATA_QUALITY is 0
        if flags_dict[k] > 0 and FLAGID2FLAG[k] != '':
            if k.startswith('ATTEN_') and int(k[-1:]) == flags_dict['ATT_STATE_AT_PEAK']:
                flags.append(FLAGID2FLAG[k].upper())
            else:
                flags.append(FLAGID2FLAG[k].replace("n", str(flags_dict[k])))
    flags.sort(key=str.lower)
    return flags


def filter_flares_by_time(flares_df, time):
    return flares_df[(flares_df["START_TIME"] < time) & (flares_df["END_TIME"] > time)]
