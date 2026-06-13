import requests
import time
import re
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from map.models import Place

# Dictionary of manual corrections for addresses that fail geocoding
MANUAL_CORRECTIONS = {
    # Typos
    "69 eur d'Aubagne, Marseille":                  "69 rue d'Aubagne, Marseille",
    "19 rtue Lafayette, Marseille":                  "19 rue Lafayette, Marseille",
    "43 ru du Patit Saint-Jean, Marseille":          "43 rue du Petit Saint-Jean, Marseille",
    "86 rue Bernard Dubois, Marseille":              "86 rue Bernard du Bois, Marseille",
    "7 rue Pollack, Marseille":                      "7 rue Rodolphe Pollack, Marseille",
    "2 rue des Feuilants, Marseille":                "2 rue des Feuillants, Marseille",
    "58 rue de Sénac de Meilhan, Marseille":         "58 rue Sénac de Meilhan, Marseille",
    "4 rue Rodolphe\xa0Pollack, Marseille":          "4 rue Rodolphe Pollack, Marseille",
    "44 \xa0rue du Tapis Vert, Marseille":           "44 rue du Tapis Vert, Marseille",
    # Méolan
    "3 Méolan / 7rue de Rome, Marseille":            "7 rue de Rome, Marseille",
    "7 rue de Rome / 3 Méolan, Marseille":           "7 rue de Rome, Marseille",
    # allées → allée
    "29 allées Léon Gambetta, Marseille":            "29 allée Léon Gambetta, Marseille",
    "55 allées Léon Gambetta, Marseille":            "55 allée Léon Gambetta, Marseille",
    "51 à 55 allées Léon Gambetta, Marseille":       "51 allée Léon Gambetta, Marseille",
    "63 allées Léon Gambetta, Marseille":            "63 allée Léon Gambetta, Marseille",
    "73 allées Léon Gambetta, Marseille":            "73 allée Léon Gambetta, Marseille",
    # Composite addresses → take first valid address
    "124-126 La Canebière / 2 rue Sénac de Meilhan, Marseille":    "124-126 La Canebière, Marseille",
    "2 rue Sénac de Meilhan / 124-126 La Canebière, Marseille":    "2 rue Sénac de Meilhan, Marseille",
    "39-41-43 rue de la Palud et 1 Domaine Ventre, Marseille":     "39-41-43 rue de la Palud, Marseille",
    "1 Domaine Ventre et 39-41-43 rue de la Palud, Marseille":     "39-41-43 rue de la Palud, Marseille",
    "3-4-8-10 Domaine Ventre, Marseille":                          "4 Domaine Ventre, Marseille",
    "24-26 place Jean Jaurès et79-81-85-92-96-98-100 rue Curiol, Marseille": "24-26 place Jean Jaurès, Marseille",
    "79 au 85 et 92 au 98 rue Curiol, Marseille":                  "79 rue Curiol, Marseille",
    "27 rue Longue des Capucins + 27 rue Vincent Scotto + 28 rue Poids de la Farine, Marseille": "27 rue Longue des Capucins, Marseille",
    "28 rue Poids de la Farine + 27 rue Longue des Capucins + 27 rue Vincent Scotto, Marseille": "28 rue Poids de la Farine, Marseille",
    "27 rue Vincent Scotto + 27 rue Longue des Capucins + 28 rue Poids de la Farine, Marseille": "27 rue Vincent Scotto, Marseille",
    "8 à 12 rue de la Fare (commerces) et 13 rue de la Fare ainsi que 20 rue des Petites Maries, Marseille": "8 rue de la Fare, Marseille",
    # Streets Nominatim doesn't find with "de/du"
    "36 rue de Chateauredon, Marseille":    "36 rue Chateauredon, Marseille",
    "40 rue du Commandant Mages, Marseille": "40 rue Commandant Mages, Marseille",
    "60 rue du Commandant Mages, Marseille": "60 rue Commandant Mages, Marseille",
    "5 rue de Lulli, Marseille":            "5 rue Lulli, Marseille",
    "7 rue de Lulli, Marseille":            "7 rue Lulli, Marseille",
    "15 rue du Tapis Vert, Marseille":      "15 rue Tapis Vert, Marseille",
    "55 rue du Tapis Vert, Marseille":      "55 rue Tapis Vert, Marseille",
    "40 rue Sainte-Bazile, Marseille":      "40 rue Saint-Bazile, Marseille",
    "4 rue Rodolphe Pollack, Marseille":    "4 rue Pollack, Marseille",
}

ALL_ARRONDISSEMENTS = [
    "1er", "2e", "3e", "4e", "5e", "6e", "7e", "8e",
    "9e", "10e", "11e", "12e", "13e", "14e", "15e", "16e",
]


class Command(BaseCommand):
    help = "Scrapes addresses from Marseille website and geocodes them"

    def scrape_addresses(self, arrondissement, soup):
        addresses = []

        for dl in soup.find_all("dl", class_="ckeditor-accordion"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")

            for dt, dd in zip(dts, dds):
                dt_text = dt.get_text(strip=True)
                if arrondissement.replace(" ", "").lower() in dt_text.replace(" ", "").lower():
                    self.stdout.write(f"  Found section: '{dt_text}'")

                    # Trova tutti i <li> dentro questo <dd>
                    for li in dd.find_all("li"):
                        text = li.get_text(strip=True)
                        # Take only the part before ":"
                        match = re.match(r"^(.+?)\s*:(.*)", text)
                        if match:
                            addr = match.group(1).strip()
                            after_colon = match.group(2)
                            # Keep only addresses that start with a number
                            if re.match(r"^\d", addr):
                                full = f"{addr}, Marseille"
                                # The last event in the history (separated by –/—)
                                # determines current status: green if it starts with "Mainlevée"
                                segments = re.split(r'\s*[–—]\s*', after_colon)
                                last_segment = segments[-1].strip()
                                is_mainlevee = bool(re.match(r'Mainlev[eé]e', last_segment))
                                if full not in [a for a, _ in addresses]:
                                    addresses.append((full, is_mainlevee))

        return addresses
    
    def split_composite_address(self, address):
        """
        Splits composite addresses into individual ones.
        Examples:
        '13 rue d'Aix et 2 rue Puvis de Chavannes, Marseille'
        '95 rue d'Aubagne / 50 cours Lieutaud, Marseille'
        '24-26 place Jean Jaurès et 79-81 rue Curiol, Marseille'
        """
        # Remove ", Marseille" at the end, we'll add it back later
        base = address.replace(", Marseille", "").strip()
        
        # Normalize separators to a common one "|"
        base = re.sub(r'\s+et\s+', '|', base, flags=re.IGNORECASE)
        base = re.sub(r'\s*/\s*', '|', base)
        base = re.sub(r'\s*\+\s*', '|', base)
        base = re.sub(r'\s+ainsi que\s+', '|', base, flags=re.IGNORECASE)
        # Handle "79 au 85" or "51 à 55" → take only first number
        base = re.sub(r'(\d+)\s+(?:au|à)\s+\d+', r'\1', base, flags=re.IGNORECASE)

        parts = base.split('|')
        
        # Rebuild each part with ", Marseille"
        result = []
        for part in parts:
            part = part.strip()
            # Remove parenthetical notes like "(commerces)"
            part = re.sub(r'\(.*?\)', '', part).strip()
            if part and re.search(r'(rue|boulevard|cours|place|avenue|impasse|chemin|montée|traverse|allée)', part, re.IGNORECASE):
                # Check if the part already contains a street type
                # (if not, it might be just a number without street name)
                    result.append(f"{part}, Marseille")
        
        return result if result else [address]  # fallback to original if splitting fails


    def geocode(self, address):
        # Check manual corrections first
        corrected = MANUAL_CORRECTIONS.get(address, address)
        if corrected != address:
            self.stdout.write(f"  Applying correction: {address} → {corrected}")
            address = corrected
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "mia-app-map/1.0"}
        response = requests.get(url, params=params, headers=headers)
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
        return None

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching page...")
        url = "https://www.marseille.fr/logement-urbanisme/amelioration-de-lhabitat/arretes-de-peril"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        addresses = []
        for arr in ALL_ARRONDISSEMENTS:
            self.stdout.write(f"Scraping arrondissement {arr}...")
            addresses.extend(self.scrape_addresses(arr, soup))
        self.stdout.write(f"Found {len(addresses)} addresses total")

        for address, is_mainlevee in addresses:
            if Place.objects.filter(address=address).exists():
                self.stdout.write(f"  Already in DB: {address}")
                continue

            self.stdout.write(f"  Geocoding: {address}")
            coords = self.geocode(address)

            # If not found, try splitting the address
            if not coords:
                self.stdout.write(f"  Trying to split composite address...")
                sub_addresses = self.split_composite_address(address)

                if len(sub_addresses) > 1:
                    self.stdout.write(f"  Split into {len(sub_addresses)} parts: {sub_addresses}")
                    for sub in sub_addresses:
                        coords = self.geocode(sub)
                        if coords:
                            self.stdout.write(f"  Found coordinates using: {sub}")
                            break
                        time.sleep(1)

            if coords:
                Place.objects.filter(address=address).delete()
                Place.objects.create(
                    address=address,
                    lat=coords[0],
                    lon=coords[1],
                    geocoded=True,
                    mainlevee=is_mainlevee,
                )
                label = " [Mainlevée]" if is_mainlevee else ""
                self.stdout.write(self.style.SUCCESS(f"  Saved: {address}{label}"))
            else:
                self.stdout.write(self.style.WARNING(f"  Not found: {address}"))
                Place.objects.create(address=address, geocoded=False)
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Done!"))