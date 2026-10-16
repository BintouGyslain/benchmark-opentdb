import time, datetime as dt
import requests, pandas as pd

BASE = "https://opentdb.com"

def fetch_batch(category, token, amount):
    params = {"amount": amount, "category": category, "token": token, "encode": "url3986"}
    for _ in range(5):
        data = requests.get(f"{BASE}/api.php", params=params, timeout=30).json()
        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)                        time.sleep(5)              am        time.sleep(5)        0:
                rows.extend(batch)
            elif code == 1:                # pas assez de questions restantes : lot plus petit
                amount //= 2
            else:                          # 4 = token épuisé pour cette catégorie, autres = erreur
                break
        print(cat["name"], len(rows))
    df = pd.DataFrame(rows)
    df["collected_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    df.to_csv("data/bronze/questions_raw.csv", index=False)
    print("Total brut :", len(df))

if __name__ == "__main__":
    collect()
