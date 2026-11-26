"""
Value Bet Detector and Kelly Criterion Staking Plan.
Identifies discrepancies between algorithmic fair odds and bookmaker market odds.
"""
from typing import Dict, Any, List, Optional

class ValueBetFinder:
    @staticmethod
    def calculate_ev(prob: float, bookmaker_odd: float) -> float:
        """
        Expected Value (EV):
        EV = (P * Odd) - 1.0
        A positive EV (> 0) represents a profitable bet in the long run.
        """
        if bookmaker_odd <= 1.0 or prob <= 0:
            return -1.0
        return (prob * bookmaker_odd) - 1.0

    @staticmethod
    def calculate_kelly(prob: float, bookmaker_odd: float, fraction: float = 0.25) -> float:
        """
        Kelly Criterion Formula:
        f* = (b*p - q) / b
        where b = bookmaker_odd - 1, p = prob, q = 1 - p.
        We apply a fractional Kelly (default 0.25 = quarter Kelly)
        for safety and volatility reduction.
        Returns recommended percentage of total bankroll (0% to 5%).
        """
        if bookmaker_odd <= 1.0 or prob <= 0 or prob >= 1.0:
            return 0.0

        b = bookmaker_odd - 1.0
        p = prob
        q = 1.0 - p

        full_kelly = (b * p - q) / b
        if full_kelly <= 0:
            return 0.0

        # Fractional Kelly capped at 5% max bankroll stake per single bet
        recommended = min(full_kelly * fraction * 100, 5.0)
        return round(recommended, 2)

    def scan_fixture(
        self,
        fixture: Dict[str, Any],
        prediction: Dict[str, Any],
        min_ev_threshold: float = 0.03 # 3% EV minimum
    ) -> List[Dict[str, Any]]:
        """
        Scans a fixture's bookmaker odds against model probabilities to extract +EV opportunities.
        """
        odds = fixture.get("odds", {})
        probs = prediction.get("probabilities", {})

        markets = [
            {"key": "home", "market": "1X2", "selection": "1 (Victoire Domicile)", "p": probs.get("home_win", 0) / 100.0, "odd": odds.get("home")},
            {"key": "draw", "market": "1X2", "selection": "X (Match Nul)", "p": probs.get("draw", 0) / 100.0, "odd": odds.get("draw")},
            {"key": "away", "market": "1X2", "selection": "2 (Victoire Extérieur)", "p": probs.get("away_win", 0) / 100.0, "odd": odds.get("away")},
            {"key": "over25", "market": "Total Buts", "selection": "Plus de 2.5 Buts", "p": probs.get("over_25", 0) / 100.0, "odd": odds.get("over25")},
            {"key": "under25", "market": "Total Buts", "selection": "Moins de 2.5 Buts", "p": probs.get("under_25", 0) / 100.0, "odd": odds.get("under25")},
            {"key": "btts_yes", "market": "Les 2 Équipes Marquent", "selection": "Oui (BTTS)", "p": probs.get("btts_yes", 0) / 100.0, "odd": odds.get("btts_yes")},
            {"key": "btts_no", "market": "Les 2 Équipes Marquent", "selection": "Non (BTTS)", "p": probs.get("btts_no", 0) / 100.0, "odd": odds.get("btts_no")}
        ]

        value_bets = []
        for m in markets:
            odd = m.get("odd")
            p = m.get("p", 0)
            if not odd or odd <= 1.0 or p <= 0:
                continue

            ev = self.calculate_ev(p, odd)
            if ev >= min_ev_threshold:
                edge = round((p - (1.0 / odd)) * 100, 2)
                kelly_stake = self.calculate_kelly(p, odd, fraction=0.25)

                confidence = "Élevée" if ev > 0.10 else "Moyenne" if ev > 0.05 else "Modérée"

                value_bets.append({
                    "fixture_id": fixture.get("id"),
                    "market": m["market"],
                    "selection": m["selection"],
                    "bookmaker_odd": odd,
                    "fair_odd": round(1.0 / p, 2),
                    "model_probability": round(p * 100, 1),
                    "implied_probability": round((1.0 / odd) * 100, 1),
                    "expected_value_pct": round(ev * 100, 2),
                    "edge_pct": edge,
                    "recommended_stake_pct": kelly_stake,
                    "confidence": confidence
                })

        value_bets.sort(key=lambda x: x["expected_value_pct"], reverse=True)
        return value_bets
