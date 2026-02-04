from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import json
import os
import re

import requests


@dataclass
class ApiCredentials:
    name: str
    api_key: str


class CredentialsResolver:
    def __init__(self, credentials_path: Optional[Path] = None) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self.credentials_path = credentials_path or (repo_root / ".moltbook" / "credentials.json")

    def resolve(self, account_name: str) -> ApiCredentials:
        env_key = self._env_key(account_name)
        api_key = os.environ.get(env_key)
        if api_key:
            return ApiCredentials(name=account_name, api_key=api_key)

        payload = self._load_credentials_file()
        accounts = payload.get("accounts", {}) if isinstance(payload, dict) else {}
        account = accounts.get(account_name)
        if isinstance(account, dict) and account.get("api_key"):
            return ApiCredentials(
                name=str(account.get("name") or account_name),
                api_key=str(account["api_key"]),
            )
        raise ValueError(f"Missing credentials for account: {account_name}")

    def _load_credentials_file(self) -> Dict[str, object]:
        if not self.credentials_path.exists():
            return {}
        with self.credentials_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _env_key(account_name: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9]+", "_", account_name).upper()
        return f"MOLTBOOK_API_KEY_{normalized}"


class MoltbookClient:
    def __init__(
        self,
        resolver: CredentialsResolver,
        base_url: str = "https://www.moltbook.com/api/v1",
        timeout: int = 60,
    ) -> None:
        self.resolver = resolver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def create_post(
        self, account: str, submolt: str, title: str, content: str
    ) -> Dict[str, object]:
        url = f"{self.base_url}/posts"
        payload = {"title": title, "content": content, "submolt": submolt}
        return self._post(account, url, payload)

    def create_comment(self, account: str, post_id: str, content: str) -> Dict[str, object]:
        url = f"{self.base_url}/posts/{post_id}/comments"
        payload = {"post_id": post_id, "content": content}
        return self._post(account, url, payload)

    def get_posts(
        self,
        account: str,
        submolt: Optional[str] = None,
        sort: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Dict[str, object]:
        url = f"{self.base_url}/posts"
        params: Dict[str, object] = {}
        if submolt:
            params["submolt"] = submolt
        if sort:
            params["sort"] = sort
        if query:
            params["q"] = query
        return self._get(account, url, params)

    def get_post(self, account: str, post_id: str) -> Dict[str, object]:
        url = f"{self.base_url}/posts/{post_id}"
        return self._get(account, url, None)

    def _post(self, account: str, url: str, payload: Dict[str, object]) -> Dict[str, object]:
        creds = self.resolver.resolve(account)
        headers = {
            "Authorization": f"Bearer {creds.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        if response.status_code in (200, 201):
            return response.json()
        return {"error": response.text, "status": response.status_code}

    def _get(
        self, account: str, url: str, params: Optional[Dict[str, object]]
    ) -> Dict[str, object]:
        creds = self.resolver.resolve(account)
        headers = {
            "Authorization": f"Bearer {creds.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        if response.status_code == 200:
            return response.json()
        return {"error": response.text, "status": response.status_code}
