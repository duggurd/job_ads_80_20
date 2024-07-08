from lib import get_ads_metadata, get_sqlalchemy_conn, get_ads_content
from requests_cache import install_cache

install_cache(expiry=-1)

# get_ads_metadata(None, "")
get_ads_content()
