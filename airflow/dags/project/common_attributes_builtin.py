from typing import List

from pymongo import MongoClient


def find_keys_intersection(cursor: List[dict])->List[str]:
    current = set(cursor[0].keys())
    print(current)
    for i in cursor:
        current = current.intersection(i.keys())
    return current

if __name__ == '__main__':
    client: MongoClient = get_mongo_client()
    dbname = client['builtin']
    companies_collection = dbname['companies']
    jobs_collection = dbname['jobs']

    companies = companies_collection.find()
    jobs = jobs_collection.find()
    inter = find_keys_intersection(jobs)
    # inter = find_keys_intersection(companies)
    for item in inter:
        print(item)
