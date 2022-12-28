import logging
import time
from dataclasses import dataclass, asdict
import requests
from urllib.parse import unquote
from pymongo import MongoClient


@dataclass
class RequestFields:
    path: str
    params: dict
    headers: dict

    def __post_init__(self):
        self.host: str = "api.builtin.com"
        self.url = f"https://{self.host}{self.path}"


JOB_CATEGORIES = [
    {
        "id": 147,
        "name": "Data + Analytics",
    },
    {
        "id": 148,
        "name": "Design + UX",
    },
    {
        "id": 149,
        "name": "Developer + Engineer",
    },
    {
        "id": 146,
        "name": "Finance",
    },
    {
        "id": 150,
        "name": "HR",
    },
    {
        "id": 151,
        "name": "Internships",
    },
    {
        "id": 152,
        "name": "Legal",
    },
    {
        "id": 153,
        "name": "Marketing",
    },
    {
        "id": 154,
        "name": "Operations",
    },
    {
        "id": 155,
        "name": "Product",
    },
    {
        "id": 156,
        "name": "Project Mgmt",
    },
    {
        "id": 157,
        "name": "Sales",
    },
    {
        "id": 158,
        "name": "Content",
    }
]

search_path = "/services/job-retrieval/legacy-collapsed-jobs"
search_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Accept": "*/*",
    "Accept-Language": "en,en-US;q=0.5",
    "Referer": "https://www.builtinla.com/",
    "Content-Type": "application/json",
    "Origin": "https://www.builtinla.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers"
}
company_path = "/companies/alias/upkeep-maintenance-management"
company_base_path = "/companies/alias/"
company_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en,en-US;q=0.5",
    # "builtin-vue-version": "1573b70b7feb6458bb9955134d8aa0b3435c243c",
    "Origin": "https://www.builtinla.com",
    "DNT": "1",
    "Connection": "keep-alive",
    'Referer': "https://www.builtinla.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers"
}

jobs_all_req = RequestFields(
    path=search_path,
    params={
        "categories": "",
        "subcategories": "",
        "experiences": "",
        "industry": "",
        "regions": "",
        "locations": unquote("9%2C41%2C10%2C12%2C11%2C13%2C14%2C15%2C50%2C16%2C17"),
        "remote": "2",
        "per_page": "10",
        "page": "1",
        "search": "",
        "sortStrategy": "recency",
        "job_locations": unquote(
            "3%7C9%2C3%7C41%2C3%7C10%2C3%7C12%2C3%7C11%2C3%7C13%2C3%7C14%2C3%7C15%2C3%7C50%2C3%7C16%2C3%7C17%2C3%7C0"),
        "company_locations": unquote(
            "3%7C9%2C3%7C41%2C3%7C10%2C3%7C12%2C3%7C11%2C3%7C13%2C3%7C14%2C3%7C15%2C3%7C50%2C3%7C16%2C3%7C17%2C3%7C0"),
        "jobs_board": "true",
        "national": "false"
    },
    headers=search_headers
)

jobs_frontend_req = RequestFields(
    path=search_path,
    params={
        "categories": "149",
        "subcategories": "520",
        "experiences": "",
        "industry": "",
        "regions": "",
        "locations": unquote("9%2C41%2C10%2C12%2C11%2C13%2C14%2C15%2C50%2C16%2C17"),
        "remote": "2",
        "per_page": "10",
        "page": "1",
        "search": "",
        "sortStrategy": "recency",
        "job_locations": unquote(
            "3%7C9%2C3%7C41%2C3%7C10%2C3%7C12%2C3%7C11%2C3%7C13%2C3%7C14%2C3%7C15%2C3%7C50%2C3%7C16%2C3%7C17%2C3%7C0"),
        "company_locations": unquote(
            "3%7C9%2C3%7C41%2C3%7C10%2C3%7C12%2C3%7C11%2C3%7C13%2C3%7C14%2C3%7C15%2C3%7C50%2C3%7C16%2C3%7C17%2C3%7C0"),
        "jobs_board": "true",
        "national": "false"
    },
    headers=search_headers
)


def make_request_for_fields(request_fields: RequestFields):
    time.sleep(3)
    return requests.get(request_fields.url,
                        params=request_fields.params,
                        headers=request_fields.headers)


def more_company_details(company):
    alias: str = company.get("alias").replace("/company/", "")
    region_id: int = company.get("region_id")
    company_req = RequestFields(
        path=f"{company_base_path}{alias}",
        params={"region_id": str(region_id)},
        headers=company_headers
    )
    res = make_request_for_fields(company_req)
    return res.json()


class BuiltinScraper:
    def __init__(self, client: MongoClient):
        self.client = client
        self.dbname = client['builtin']
        self.companies_collection = self.dbname['companies']
        self.jobs_collection = self.dbname['jobs']

    def process_request_for_search(self, res: requests.Response):
        company_jobs = res.json().get("company_jobs")
        for cj in company_jobs:
            company = cj.get("company")
            self.save_company_if_not_exists(company)
            jobs = cj.get("jobs")
            for j in jobs:
                self.save_job_if_not_exists(j)

    def save_company_if_not_exists(self, company: dict):
        existing = self.companies_collection.find_one(filter={"id": company.get("id")})
        if not existing:
            company.update(more_company_details(company))
            self.companies_collection.insert_one(company)
            logging.info(f"Saved company id:{company['id']}")

    def save_job_if_not_exists(self, job):
        existing = self.jobs_collection.find_one(filter={"id": job.get("id")})
        if not existing:
            self.jobs_collection.insert_one(job)
            logging.info(f"Saved job id:{job['id']}")

    def run(self):
        res = make_request_for_fields(jobs_frontend_req)
        data = res.json()
        page_count = data.get("pagination_count", 1)
        logging.info(f"page_count {page_count}")
        self.process_request_for_search(res)
        for p in range(2, page_count + 1):
            logging.info(f"Page {p}")
            jobs_frontend_req.params.update({"page": str(p)})
            res = make_request_for_fields(jobs_frontend_req)
            self.process_request_for_search(res)
        logging.info("Done")


def get_mongo_client()-> MongoClient:
    import os
    from dotenv import load_dotenv

    load_dotenv()
    MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    MONGO_HOST = "localhost"
    MONGO_PORT = os.getenv('MONGO_PORT')

    CONNECTION_STRING = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/admin"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    return MongoClient(CONNECTION_STRING)

if __name__ == '__main__':
    client = get_mongo_client()

    scraper = BuiltinScraper(client)
    scraper.run()
