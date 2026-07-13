import os
import requests
import tarfile
from urllib.parse import urljoin
from bs4 import BeautifulSoup  # pip install beautifulsoup4

BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_daily/bils/p05/"

def list_years():
    """Return list of available year folders."""
    r = requests.get(BASE_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    years = [a.get("href").strip("/") for a in soup.find_all("a") if a.get("href").strip("/").isdigit()]
    return years

def list_files(year):
    """List all daily .tar.gz files for a given year."""
    year_url = urljoin(BASE_URL, f"{year}/")
    r = requests.get(year_url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    files = [urljoin(year_url, a.get("href")) for a in soup.find_all("a") if a.get("href", "").endswith(".tar.gz")]
    return files

def download_and_extract(url, out_dir):
	"""Download a daily tar.gz file and extract to out_dir."""
	local_name = os.path.join(out_dir, os.path.basename(url))
	#print(local_name)
	if os.path.exists(local_name.replace(".tar.gz", ".bil")):
		print(f"Skipping {url} (already extracted)")
		return
	print(f"Downloading {url}")
	r = requests.get(url, stream=True)
	r.raise_for_status()
	os.makedirs(out_dir, exist_ok=True)
	tmp_path = local_name + ".part"
	with open(tmp_path, "wb") as f:
		for chunk in r.iter_content(chunk_size=8192):
			f.write(chunk)
#    with tarfile.open(tmp_path, "r:gz") as tar:
#        tar.extractall(path=out_dir)
#    os.remove(tmp_path)
	print(f"Extracted {url} ? {out_dir}")

def main(years=None, out_root="chirps_africa"):
    all_years = list_years()
    if years is None:
        years = all_years
    for year in years:
        if year not in all_years:
            print(f"Skipping {year}, not found on server")
            continue
        out_dir = os.path.join(out_root, year)
        os.makedirs(out_dir, exist_ok=True)
        urls = list_files(year)
        print(f"Year {year}: {len(urls)} daily files")
        for url in urls:
            download_and_extract(url, out_dir)

if __name__ == "__main__":
	#path_output = "/share/home/c1755103/dataset/CHIRPS/"
	path_output = "/user/work/km19051/dataset/CHIRPS/raw/"
	# Example: download years 1981 and 1982 only
	main(out_root=path_output)
	#main(years=["1981"], out_root=path_output)
	# Or to download all: main()
