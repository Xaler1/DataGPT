from bs4 import BeautifulSoup as bsoup
import requests
from src.gpt_function import gpt_function
from agents.summarizer import html_extract

@gpt_function
def get_cik(company: str):
    """
    Useful for getting the CIK of a company.
    :param company: the name of the company to look for
    """

    params = {"company": company}
    url = "https://www.sec.gov/cgi-bin/cik_lookup"
    req = requests.get(url, params=params)
    if req.status_code != 200:
        return {"result": f"HTTP REQUEST ERROR!: {req.status_code}"}
    else:
        soup = bsoup(req.content, "html5lib")
        body = soup.find("tbody")
        table = body.find("tr")
        head = table.find("hr")
        rows = head.next_sibling
        companies = list(rows.strings)
        filtered = {"candidates": []}
        print("-----------------")
        for i in range(min(len(companies), 20)):
            name = companies[i].replace("\n", "").replace("\t", "")
            cik = companies[i - 1].replace("\n", "")
            if cik.isnumeric():
                print(name, cik)
                filtered["candidates"].append({
                    "name": name,
                    "cik": cik
                })
        return filtered


@gpt_function
def get_company_info(cik: str):
    """
    Useful for getting the details of a company. The address, phone number, website, and number of recent filings.
    :param cik: the CIK of a company. Do not invent, use get_cik to get the CIK of a company.
    """

    response = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers={"User-Agent": "test test"})
    if response.status_code != 200:
        return {"result": f"HTTP REQUEST ERROR!: {response.status_code}"}
    else:
        data = response.json()
        address = data["addresses"]["business"]
        return {
            "name": data["name"],
            "website": data["website"],
            "address": f"{address['street2']}, {address['street1']}, {address['city']}, {address['stateOrCountry']}, {address['zipCode']}",
            "phone": data["phone"],
            "number_of_recent_filings": len(data["filings"]["recent"]["accessionNumber"]),
        }


@gpt_function
def get_company_filings(cik: str, max_results: int = 20):
    """
    Useful for getting the index of the filings of a company. Can be used to get the accession number of a filing.
    Basic info in filings involving their date and form type.
    :param cik: the CIK of a company
    :param max_results: the maximum number of results to return, optional integer
    """

    response = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers={"User-Agent": "test test"})
    if response.status_code != 200:
        return {"result": f"HTTP REQUEST ERROR!: {response.status_code}"}
    else:
        data = response.json()
        filings = data["filings"]["recent"]
        filtered = {"filings": []}
        for i in range(min(len(filings["accessionNumber"]), max_results)):
            filtered["filings"].append({
                "accessionNumber": filings["accessionNumber"][i],
                "filingDate": filings["filingDate"][i],
                "form": filings["form"][i],
                "url": f"https://www.sec.gov/Archives/edgar/data/{cik.replace('000', '')}/{filings['accessionNumber'][i].replace('-', '')}/{filings['primaryDocument'][i]}"
            })
        return filtered

@gpt_function
def get_full_filing(cik: str, accession_number: str):
    """
    Useful for getting the full version of a particular filing.
    Can get all the information in the filing.
    :param cik: the CIK of a company
    :param accession_number: the accession number of the filing
    """

    response = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers={"User-Agent": "test test"})
    if response.status_code != 200:
        return {"result": f"HTTP REQUEST ERROR!: {response.status_code}"}
    else:
        data = response.json()
        filings = data["filings"]["recent"]
        for i in range(len(filings["accessionNumber"])):
            if filings["accessionNumber"][i] == accession_number:
                primaryDocument = filings["primaryDocument"][i]
                break

    url = f"https://www.sec.gov/Archives/edgar/data/{cik.replace('000', '')}/{accession_number.replace('-', '')}/{primaryDocument}"
    print(url)
    response = requests.get(url, headers={"User-Agent": "test test"})
    if response.status_code != 200:
        return {"result": f"HTTP REQUEST ERROR!: {response.status_code}"}
    else:
        data = response.text
        text = html_extract(data)
        summarized = html_extract(text)
        return {"summarization": summarized}


