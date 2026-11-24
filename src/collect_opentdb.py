"""Collect all available OpenTDB questions into the bronze CSV dataset."""

import datetime as dt
import time
from pathlib import Path
from typing import Any

import requests
import pandas as pd

BASE_URL = "https://opentdb.com"
MAX_AMOUNT = 50  # OpenTDB allows at most 50 questions per request.
MIN_REQUEST_INTERVAL = 5.1  # The API rate limit is one request per 5 seconds.
RETRY_LIMIT = 5
OUTPUT = Path(__file__).resolve().parents[1] / "data/bronze/questions_raw.csv"
QUESTION_COLUMNS = [
    "type",
    "difficulty",
    "category",
    "question",
    "correct_answer",
    "incorrect_answers",
]


class OpenTDBClient:
    """Small rate-limited client for the OpenTDB API."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self._last_request = 0.0

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        for attempt in range(RETRY_LIMIT):
            delay = MIN_REQUEST_INTERVAL - (time.monotonic() - self._last_request)
            if delay > 0:
                time.sleep(delay)

            try:
                response = self.session.get(url, params=params, timeout=30)
                self._last_request = time.monotonic()
                response.raise_for_status()
                data = response.json()
            except (requests.RequestException, ValueError) as exc:
                if attempt == RETRY_LIMIT - 1:
                    raise RuntimeError(f"Échec de la requête OpenTDB ({url}): {exc}") from exc
                time.sleep(MIN_REQUEST_INTERVAL * (attempt + 1))
                continue

            # Response code 5 means the API rate limit was reached.
            if data.get("response_code") == 5:
                if attempt == RETRY_LIMIT - 1:
                    raise RuntimeError("OpenTDB a maintenu la limite de débit après plusieurs essais.")
                time.sleep(MIN_REQUEST_INTERVAL * (attempt + 1))
                continue
            return data

        raise RuntimeError(f"Impossible de contacter OpenTDB ({url}).")


def create_token(client: OpenTDBClient) -> str:
    data = client.get("api_token.php", {"command": "request"})
    if data.get("response_code") != 0 or not data.get("token"):
        raise RuntimeError(f"OpenTDB n’a pas fourni de token de session : {data}")
    return data["token"]


def fetch_category(
    client: OpenTDBClient,
    category_id: int,
    token: str,
) -> list[dict[str, Any]]:
    """Fetch available questions in one category, reducing the batch at its end."""
    rows: list[dict[str, Any]] = []
    amount = MAX_AMOUNT

    while True:
        data = client.get(
            "api.php",
            {
                "amount": amount,
                "category": category_id,
                "token": token,
                "encode": "url3986",
            },
        )
        code = data.get("response_code")

        if code == 0:
            batch = data.get("results", [])
            if not batch:
                break
            rows.extend(batch)
            amount = MAX_AMOUNT
        elif code == 1:
            # The category has fewer remaining questions than requested.
            if amount == 1:
                break
            amount = max(1, amount // 2)
        elif code == 4:
            # The session token has already returned every available question.
            break
        elif code == 3:
            raise RuntimeError("Le token de session OpenTDB est invalide ou expiré.")
        else:
            raise RuntimeError(f"Réponse OpenTDB inattendue (code {code}) pour la catégorie {category_id}.")

    return rows


def collect() -> int:
    client = OpenTDBClient()
    categories_data = client.get("api_category.php")
    categories = categories_data.get("trivia_categories", [])
    if not categories:
        raise RuntimeError("OpenTDB n’a retourné aucune catégorie.")

    token = create_token(client)
    questions: list[dict[str, Any]] = []
    for category in categories:
        category_rows = fetch_category(client, category["id"], token)
        questions.extend(category_rows)
        print(f"{category['name']} : {len(category_rows)} questions")

    collected_at = dt.datetime.now(dt.timezone.utc).isoformat()
    df = pd.DataFrame(questions, columns=QUESTION_COLUMNS)
    df["collected_at"] = collected_at
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Total brut : {len(df)} questions enregistrées dans {OUTPUT}")
    return len(df)


if __name__ == "__main__":
    collect()
