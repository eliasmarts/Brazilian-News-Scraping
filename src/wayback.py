import requests
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def _generate_timestamps(start_date, end_date, interval_days):
    """
    Generate timestamps in the format YYYYMMDDhhmmss between start_date and end_date with the given interval in days.
    """
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    interval = timedelta(days=interval_days)
    
    timestamps = []
    current = start
    while current <= end:
        timestamps.append(current.strftime("%Y%m%d%H%M%S"))
        current += interval
    return timestamps


def _query_wayback(url, timestamp):
    """
    Query the Wayback Machine API with a given URL and timestamp.
    """
    api_url = f"http://archive.org/wayback/available?url={url}&timestamp={timestamp}"
    response = requests.get(api_url)
    return response.json()


def _parse_responses(responses: list[str]) -> pd.DataFrame:
    """
    Parse the JSON resposes to obtain the URL and timestamps where the saved snapshots are avaliable
    """
    urls = []
    timestamps = []
    for response in responses:
        try:
            snapshot = response['archived_snapshots']['closest']
            
            if snapshot['status'] == '200' and snapshot['available']:
                urls.append(snapshot['url'])
                timestamps.append(snapshot['timestamp'])
        
        # not avaliable snapshot
        except Exception:
            continue
        
    links = pd.DataFrame({
        'url': urls,
        'timestamp': timestamps
    })

    links.drop_duplicates(subset=['timestamp'])

    return links
    
    
def obtain_wayback_links(url: str, start_date: str, end_date: str, interval_days: int) -> pd.DataFrame:
    """Obtain Wayback Machine links for the snapshots in a given time period

    Parameters
    ----------
    url : str
        URL of the page to look for
    start_date : str
        Start of the interval in YYYYMMDD format
    end_date : str
        End of the interval in YYYYMMDD format
    interval_days : int
        the interval of days to split the time period

    Returns
    -------
    pd.DataFrame
        DataFrame containing 'url' and 'timestamp' as columns
    """
    responses = []

    logger.info('Obtaining links')

    timestamps = _generate_timestamps(start_date, end_date, interval_days)
    for i, timestamp in enumerate(timestamps):
        response = _query_wayback(url, timestamp)
        responses.append(response)
        logger.info(f'Request {i + 1}/{len(timestamps)}', end='\r')
        
    return _parse_responses(responses)