from requests import get
from bs4 import BeautifulSoup
from time import sleep
import csv
# from IPython.core.display import clear_output


# data scraper based on finance.yahoo.com

def get_entries():
    # get company names and sectors from the list of S&P 500 companies
    src_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    content = get_content(src_url)

    table = content.find(
        "table", {"class": "wikitable sortable"}).find("tbody")

    all_companies = []
    for tr in table.findAll("tr")[1:]:
        # TODO: can also include sector
        attributes = tr.findAll("td")

        label = attributes[0].a.text
        sector = attributes[3].text

        all_companies.append((label, sector))

    return all_companies


def get_content(url):
    resp = get(url)
    return BeautifulSoup(resp.text, 'html.parser')


def extract_summary(url):
    content = get_content(url)
    summary_div = content.find("div", {"id": "quote-summary"})
    summary = {}
    for div in summary_div.findAll("div"):
        if (div.table is None):
            continue
        for tr in div.table.tbody.findAll("tr"):
            (name_td, value_td) = tr.findAll("td")
            summary[name_td.find("span").text] = value_td.text
    return summary


def extract_stats(url):
    content = get_content(url)
#   find("div", {"id": "Main"})
    stats_div = content.find("div", {"class": "Mstart(a) Mend(a)"})

    stats = {}
    for table in stats_div.findAll("table"):
        #     print (div["class"])
        for tr in table.find("tbody").findAll("tr"):
            (name_td, value_td) = tr.findAll("td")
            stats[name_td.find("span").text] = value_td.text

    return stats


def main():
    target_companies = get_entries()
    out_path = "data.csv"
    # target_companies = all_companies[:1]

    with open(out_path, "a+") as file:
        for i, (company, sector) in enumerate(target_companies[67:]):
            print (company)
            summary_url = "https://finance.yahoo.com/quote/{}?p={}". \
                format(company, company)
            stats_url = \
                "https://finance.yahoo.com/quote/{}/key-statistics?p={}". \
                format(company, company)
            summary = extract_summary(summary_url)
            stats = extract_stats(stats_url)

            if (i == 0):
                # header
                fieldnames = ["Company", "Sector"] + [*summary] + [*stats]
                csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
                csv_writer.writeheader()

            csv_writer.writerow({"Company": company,
                                 "Sector": sector,
                                 **summary, **stats})

        # sleep(1)
        # clear_output(wait=True)
    return


if __name__ == "__main__":
    main()
