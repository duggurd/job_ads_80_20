import os
import time
import sqlalchemy
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs

# if os.environ.get("ENVIRONMENT") == "development":
#     from requests_cache import install_cache, NEVER_EXPIRE
#     install_cache(expire_after=NEVER_EXPIRE)

def get_sqlalchemy_conn():
    connection_string = os.environ["CONN_INGESTION_DB"]
    return sqlalchemy.create_engine(connection_string).connect()

def get_ads_metadata(occupation=None, published:str="1"):
    if occupation is None:
       occupation = "0.23"
    
    data = get_finn_metdata_page(1, occupation, published)

    df = pd.DataFrame(data["docs"])

    paging = data["metadata"]["paging"]

    if paging["last"] > 1:
        for page in range(1, paging["last"] + 1):
            data = get_finn_metdata_page(page, occupation, published)
            df = pd.concat([df, pd.DataFrame(data["docs"])])
    print(df.head())
    if "coordinates" in df.columns:
        df["longitude"] = df["coordinates"].apply(lambda x: x.get("lon"))
        df["latitude"] =  df["coordinates"].apply(lambda x: x.get("lat")) 
    
    df["created_at"] = datetime.now()

    df = df.drop(columns=["coordinates", "logo", "labels", "flags", "image", "extras"])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["published"] = pd.to_datetime(df["published"])
    df["deadline"] = pd.to_datetime(df["deadline"])

    df["occupation"] = occupation

    conn = get_sqlalchemy_conn()

    ret = df.to_sql(
        "finn_job_ads__metadata", 
        con=conn, 
        schema="finn",
        if_exists="append", 
        index=False
    )

    print(f"inserted {ret} rows into finn_job_ads__metadata")
    conn.close()


def get_finn_metdata_page(page, occupation, published:str="1"):
    URL = f"https://www.finn.no/api/search-qf?searchkey=SEARCH_ID_JOB_FULLTIME&occupation={occupation}&q=&published={published}&vertical=job&page={page}"
    resp = requests.get(URL)  
    print(f"[{resp.status_code}]", URL)
    if not resp.ok:
        raise Exception(f"Error fetching data from {URL}: {resp.content}")

    data = resp.json()
    return data


def get_ads_content():
    # get new finnkodes
    conn = get_sqlalchemy_conn()

    res = conn.execute(text("""
        SELECT canonical_url, id 
        FROM finn.finn_job_ads__metadata AS metadata 
--        WHERE 
--            metadata.created_at > (
--                SELECT MAX(content.created_at) 
--                FROM finn.finn_job_ads__content AS content
--            ) 
--            OR (
--                SELECT MAX(contnent.created_at) 
--                FROM finn.finn_job_ads__content AS contnent
--            ) IS NULL
        ;

    """))
    rows = res.fetchall()

    for row in rows:

        data = []
        canonical_url = row[0]
        finnkode = row[1]
        try:
            html = get_ad_html(canonical_url)
        except Exception as e:
            print(e)
            continue

        record = parse_ad_html(html)

        record["id"] = finnkode

        data.append(record)

        df = pd.DataFrame(data)
        df["created_at"] = datetime.now()
        
        ret = df.to_sql(
            "finn_job_ads__content", 
            con=conn, 
            schema="finn",
            if_exists="append", 
            index=False
        )

        print(f"inserted {ret} rows into finn_job_ads__content")
        time.sleep(0.5)
    conn.close()

def get_ad_html(canonical_url: str):

    resp = requests.get(canonical_url)
    if not resp.ok:
        raise Exception(f"Error fetching data from {canonical_url}: {resp.status_code}")

    return resp.content

def parse_ad_html(html):
    record = {}
    soup = bs(html, "html.parser")
    #if add_type == "part_time":
    #   general_info = "test"

    # else:
    general_info = soup.find_all("section")[1]
    main_article = soup.find_all("section")[2]
    job_provider_info = soup.find_all("section")[3]
    keywords_section = soup.find_all("section")[4]
    
    # keywords
    keywords = keywords_section.find("p").text if keywords_section.find("p") else None
    record["keywords"] = keywords
    
    # general info
    
    for li in job_provider_info.find("ul"):
        kv = li.text.split(":")
    
        key = kv[0].strip().lower().replace(" ", "_")
    
        if key not in [
            "nettverk", 
            "sektor", 
            "hjemmekontor", 
            "bransje", 
            "stillingsfunksjon", 
            "arbeidsspråk", 
            "flere_arbeidssteder"
        ]: continue
        value = kv[1].strip()
        record[key] = value
    
    # due_date
    work_title = general_info.find("div").find("h2").text
    record["job_title"] = work_title
    
    # ad content
    # need to handle ul/li tags
    ad_content = main_article.find("div")
    
    contents = []
    
    for object in ad_content:
        if object.name == "ul":
            for li in object.find_all("li"):
                contents.append(li.text)
        else:
            contents.append(object.text)
    
    record["content"] = " ".join(contents)

    return record
