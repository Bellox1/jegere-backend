"""
Dixon-Coles Statistical Football Prediction Model.
Implements the bivariate Poisson formulation with low-scoring correlation adjustment
(Dixon & Coles 1997).
"""
import math
import numpy as np
from typing import Dict, Any, List, Tuple

class DixonColesModel:
    def __init__(self, rho: float = -0.13):
        """
        rho: low scoring correlation factor (typically between -0.10 and -0.15 for European leagues)
        """
        self.rho = rho

    @staticmethod
    def _poisson_pmf(k: int, lmbda: float) -> float:
        """Standard Poisson probability mass function"""
        if lmbda <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

    def _tau(self, x: int, y: int, lmbda: float, mu: float) -> float:
        """
        Dixon-Coles adjustment factor for low-scoring matches:
        Modulates joint probabilities for (0,0), (0,1), (1,0), and (1,1).
        """
        if x == 0 and y == 0:
            return 1.0 - (lmbda * mu * self.rho)
        elif x == 0 and y == 1:
            return 1.0 + (lmbda * self.rho)
        elif x == 1 and y == 0:
            return 1.0 + (mu * self.rho)
        elif x == 1 and y == 1:
            return 1.0 - self.rho
        else:
            return 1.0

    def calculate_xg(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        avg_home_goals: float = 1.55,
        avg_away_goals: float = 1.25,
        home_advantage: float = 1.15,
        neutral_venue: bool = False
    ) -> Tuple[float, float]:
        """
        Computes expected goals (xG) for home and away teams.
        Formula:
          lambda_home = home_attack * away_defense * (home_adv if not neutral else 1.0) * avg_home_goals
          mu_away     = away_attack * home_defense * avg_away_goals
        """
        venue_mult = 1.0 if neutral_venue else home_advantage
        lambda_home = max(0.2, home_attack * away_defense * venue_mult * (avg_home_goals / 1.50))
        mu_away = max(0.2, away_attack * home_defense * (avg_away_goals / 1.25))

        return round(lambda_home, 2), round(mu_away, 2)

    def predict_match(
        self,
        home_team: Dict[str, Any],
        away_team: Dict[str, Any],
        league_meta: Dict[str, Any],
        neutral_venue: bool = False,
        max_goals: int = 7
    ) -> Dict[str, Any]:
        """
        Computes full probability matrix and betting market outcomes.
        """
        avg_home = league_meta.get("avg_home_goals", 1.55)
        avg_away = league_meta.get("avg_away_goals", 1.25)
        home_adv = league_meta.get("home_advantage", 1.15)

        lmbda, mu = self.calculate_xg(
            home_attack=home_team.get("attack", 1.0),
            home_defense=home_team.get("defense", 1.0),
            away_attack=away_team.get("attack", 1.0),
            away_defense=away_team.get("defense", 1.0),
            avg_home_goals=avg_home,
            avg_away_goals=avg_away,
            home_advantage=home_adv,
            neutral_venue=neutral_venue
        )

        # Build joint probability matrix
        prob_matrix = np.zeros((max_goals + 1, max_goals + 1))
        for x in range(max_goals + 1):
            p_x = self._poisson_pmf(x, lmbda)
            for y in range(max_goals + 1):
                p_y = self._poisson_pmf(y, mu)
                tau_factor = self._tau(x, y, lmbda, mu)
                prob_matrix[x, y] = max(0.0, p_x * p_y * tau_factor)

        # Normalize matrix so total sum = 1.0
        total_p = np.sum(prob_matrix)
        if total_p > 0:
            prob_matrix /= total_p

        # Aggregate outcomes
        p_home_win = float(np.sum(np.tril(prob_matrix, -1)))
        p_draw = float(np.sum(np.diag(prob_matrix)))
        p_away_win = float(np.sum(np.triu(prob_matrix, 1)))

        # Goals markets
        p_over_15 = 0.0
        p_over_25 = 0.0
        p_over_35 = 0.0
        p_btts_yes = 0.0

        score_probabilities: List[Dict[str, Any]] = []

        for x in range(max_goals + 1):
            for y in range(max_goals + 1):
                p = float(prob_matrix[x, y])
                if x + y > 1.5:
                    p_over_15 += p
                if x + y > 2.5:
                    p_over_25 += p
                if x + y > 3.5:
                    p_over_35 += p
                if x >= 1 and y >= 1:
                    p_btts_yes += p

                score_probabilities.append({
                    "score": f"{x}-{y}",
                    "home_goals": x,
                    "away_goals": y,
                    "probability": round(p * 100, 2)
                })

        score_probabilities.sort(key=lambda s: s["probability"], reverse=True)

        # Heatmap matrix up to 5x5 for frontend visualization
        heatmap = []
        for x in range(5):
            row = []
            for y in range(5):
                row.append(round(float(prob_matrix[x, y]) * 100, 2))
            heatmap.append(row)

        # Elo rating diff (BeSoccer 0-100 scale)
        elo_home = home_team.get("elo", 80)
        elo_away = away_team.get("elo", 80)
        elo_diff = elo_home - elo_away

        # Clean sheet probabilities (away goals == 0 / home goals == 0)
        p_clean_sheet_home = float(np.sum(prob_matrix[:, 0]))
        p_clean_sheet_away = float(np.sum(prob_matrix[0, :]))

        return {
            "model": "Dixon-Coles & Bivariate Poisson",
            "expected_goals": {
                "home_xg": lmbda,
                "away_xg": mu,
                "total_xg": round(lmbda + mu, 2)
            },
            "probabilities": {
                "home_win": round(p_home_win * 100, 2),
                "draw": round(p_draw * 100, 2),
                "away_win": round(p_away_win * 100, 2),
                "double_chance_1x": round((p_home_win + p_draw) * 100, 2),
                "double_chance_12": round((p_home_win + p_away_win) * 100, 2),
                "double_chance_x2": round((p_draw + p_away_win) * 100, 2),
                "over_15": round(p_over_15 * 100, 2),
                "under_15": round((1.0 - p_over_15) * 100, 2),
                "over_25": round(p_over_25 * 100, 2),
                "under_25": round((1.0 - p_over_25) * 100, 2),
                "over_35": round(p_over_35 * 100, 2),
                "under_35": round((1.0 - p_over_35) * 100, 2),
                "btts_yes": round(p_btts_yes * 100, 2),
                "btts_no": round((1.0 - p_btts_yes) * 100, 2),
                "clean_sheet_home": round(p_clean_sheet_home * 100, 2),
                "clean_sheet_away": round(p_clean_sheet_away * 100, 2)
            },
            "fair_odds": {
                "home": round(1.0 / p_home_win, 2) if p_home_win > 0 else 99.0,
                "draw": round(1.0 / p_draw, 2) if p_draw > 0 else 99.0,
                "away": round(1.0 / p_away_win, 2) if p_away_win > 0 else 99.0,
                "over_25": round(1.0 / p_over_25, 2) if p_over_25 > 0 else 99.0,
                "under_25": round(1.0 / (1.0 - p_over_25), 2) if p_over_25 < 1.0 else 99.0,
                "btts_yes": round(1.0 / p_btts_yes, 2) if p_btts_yes > 0 else 99.0,
                "btts_no": round(1.0 / (1.0 - p_btts_yes), 2) if p_btts_yes < 1.0 else 99.0
            },
            "top_scores": score_probabilities[:6],
            "heatmap_matrix": heatmap,
            "elo_diff": elo_diff
        }
