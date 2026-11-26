## Je Gère ⚽📊

> Système de prédiction et d'analyse statistique avancé dans le domaine du football, développé en **Angular 22** avec un module **Python FastAPI** pour les calculs stochastiques lourds (Dixon-Coles & Monte Carlo).

---

## 🌟 Points Forts & Architecture Hybride

L'application a été conçue selon une architecture **hybride intelligente** :

1. **Frontend Angular 22 (Standalone & Moderne)** :
   - Interface de pointe type analytics sportive (Thème sombre glassmorphism, typographies Inter/Outfit, graphismes fluides).
   - **Moteur statistique autonome en TypeScript** : intègre le calcul des probabilités de Poisson, l'estimation des Expected Goals (xG), la matrice de Dixon-Coles, la détection des Value Bets (+EV) et un simulateur Monte Carlo client. L'application peut donc fonctionner **à 100% de façon autonome dans le navigateur** même si Python n'est pas lancé !
   - Gestion d'état réactive basée sur les **Signals Angular** et `provideHttpClient()`.

2. **Module Backend Python (FastAPI, SciPy, NumPy)** :
   - Dédié aux tâches que le frontend ne peut pas ou ne doit pas exécuter seul :
     - Modélisation mathématique **Dixon-Coles** avec paramètre d'ajustement de corrélation $\rho = -0.13$ pour les scores nuls et faibles.
     - Simulations stochastiques de **Monte Carlo intensives (10 000 à 50 000 matchs)** avec modélisation minute par minute des événements (cartons rouges, fatigue en fin de match, penalties).
     - Proxy sécurisé pour contourner les restrictions CORS des API de football et protéger vos clés d'API.

---

## 📐 Modèles Mathématiques & Techniques Implémentés

### 1. Modèle de Dixon & Coles (1997)
Le modèle classique de Poisson suppose l'indépendance entre les buts de l'équipe à domicile et ceux de l'équipe à l'extérieur. Dans la réalité, les scores (0-0), (1-0), (0-1) et (1-1) sont sous-évalués par un Poisson pur. Dixon-Coles applique un facteur de correction $\tau_{x,y}$ :
$$\tau_{0,0} = 1 - \lambda \mu \rho$$
$$\tau_{0,1} = 1 + \lambda \rho$$
$$\tau_{1,0} = 1 + \mu \rho$$
$$\tau_{1,1} = 1 - \rho$$

### 2. Expected Goals (xG)
$$\lambda_{dom} = \text{ForceAttaque}_{dom} \times \text{FaiblesseDéfense}_{ext} \times \text{AvantageDomicile} \times \text{MoyenneButsDom}$$
$$\mu_{ext} = \text{ForceAttaque}_{ext} \times \text{FaiblesseDéfense}_{dom} \times \text{MoyenneButsExt}$$

### 3. Simulation Stochastique de Monte Carlo (10 000 itérations)
Simule 10 000 fois la rencontre en introduisant la variance en match : probabilité de carton rouge (~7%), baisse de rendement numérique (-30% xG pour l'équipe pénalisée, +20% pour l'adversaire), distribution des corners et des cartons.

### 4. Détecteur de Value Bets (+EV) & Formule de Kelly
$$\text{Expected Value (EV)} = (P_{modèle} \times \text{Cote}_{bookmaker}) - 1$$
$$\text{Critère de Kelly Fractionnaire} : f^* = \frac{b \cdot p - q}{b} \times 0.25$$

---

## 🚀 Fonctionnalités Clés de l'Application

- 📊 **Tableau de Bord** : Match phare de la journée, KPIs clés (taux de réussite, ROI backtesté à +14.2%, nombre de value bets actifs), top opportunités à forte espérance mathématique.
- ⚽ **Matchs & Pronostics** : Filtrage par ligues (Premier League, La Liga, Ligue 1, Serie A, Bundesliga, Champions League), badge Value Bet, cotes réelles vs cotes justes du modèle.
- 🎯 **Détail Analytique & Matrice de Chaleur** :
  - **Heatmap 5x5 interactive des scores exacts** avec intensité de couleur basée sur la probabilité.
  - Marchés Plus/Moins de 1.5, 2.5, 3.5 buts, Les 2 Équipes Marquent (BTTS), Double Chance.
  - Lanceur de simulation Monte Carlo 10 000 matchs en direct.
- 🔬 **Simulateur "What-If"** : Bac à sable permettant d'opposer n'importe quelles équipes (même de championnats différents), d'ajuster les coefficients d'attaque et de défense avec des sliders, d'activer le terrain neutre et d'observer instantanément les probabilités recalculées.
- 💎 **Scanner de Value Bets** : Filtrage par espérance minimale (+EV%), tri par edge et calcul de la mise optimale selon Kelly.
- 💼 **Gestionnaire de Bankroll** : Journal de paris persistant en `localStorage`, calcul automatique du capital actuel, du taux de réussite (Win Rate) et du retour sur investissement (ROI).
- ⚙️ **Paramètres & Connectivité API** : Bascule 1-clic entre Moteur Python FastAPI et Moteur Angular Client, champs pour clés Football-Data.org / API-Football (RapidAPI), et configuration de la taille de bankroll.

---

## 🛠️ Installation et Démarrage

### Prérequis
- **Node.js** (v18+) et **npm**
- **Python** (3.10+) avec `fastapi`, `uvicorn`, `numpy`, `scipy`, `requests`

### Démarrage Automatique (Recommandé)
Double-cliquez sur :
```bash
start.bat
```
ou exécutez sous PowerShell :
```powershell
.\start.ps1
```

### Démarrage Manuel

#### 1. Lancer le Backend Python FastAPI :
```powershell
python backend/run.py
```
*Le serveur démarrera sur l'URL configurée dans `.env` (`BACKEND_URL`).*

#### 2. Lancer le Frontend Angular :
Dans un autre terminal :
```powershell
cd frontend
npm start
```
*L'application s'ouvrira sur l'adresse du serveur Angular configurée.*
