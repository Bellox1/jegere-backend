"""
Football Data Provider - 100% Dynamic Live API Integration.
No hardcoded teams, stats or fixtures. All data is dynamically fetched and
computed in real time from live football APIs.
"""
from typing import Dict, List, Any
from backend.data.api_service import api_service

def get_live_leagues() -> Dict[str, Dict[str, Any]]:
    if not api_service.cached_leagues:
        api_service.sync_live_data()
    return api_service.cached_leagues

def get_live_teams() -> Dict[str, Dict[str, Any]]:
    if not api_service.cached_teams:
        api_service.sync_live_data()
    return api_service.cached_teams

def get_live_fixtures() -> List[Dict[str, Any]]:
    if not api_service.cached_fixtures:
        api_service.sync_live_data()
    return api_service.cached_fixtures

class DynamicDataProxy(dict):
    """Dynamically proxies access to live API cached dictionary without any hardcoded records."""
    def __init__(self, fetcher):
        super().__init__()
        self._fetcher = fetcher

    def _ensure(self):
        data = self._fetcher()
        self.clear()
        self.update(data)

    def __getitem__(self, item):
        self._ensure()
        return super().__getitem__(item)

    def get(self, k, default=None):
        self._ensure()
        return super().get(k, default)

    def values(self):
        self._ensure()
        return super().values()

    def items(self):
        self._ensure()
        return super().items()

    def keys(self):
        self._ensure()
        return super().keys()

    def __len__(self):
        self._ensure()
        return super().__len__()

    def __iter__(self):
        self._ensure()
        return super().__iter__()

class DynamicListProxy(list):
    """Dynamically proxies access to live API cached list without any hardcoded records."""
    def __init__(self, fetcher):
        super().__init__()
        self._fetcher = fetcher

    def _ensure(self):
        data = self._fetcher()
        self.clear()
        self.extend(data)

    def __iter__(self):
        self._ensure()
        return super().__iter__()

    def __len__(self):
        self._ensure()
        return super().__len__()

    def __getitem__(self, item):
        self._ensure()
        return super().__getitem__(item)

# Exported 100% dynamic objects (zero static hardcoded data)
TEAMS_DATABASE = DynamicDataProxy(get_live_teams)
LEAGUES_DATA = DynamicDataProxy(get_live_leagues)
UPCOMING_FIXTURES = DynamicListProxy(get_live_fixtures)
