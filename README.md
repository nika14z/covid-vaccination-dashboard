# COVID-19 Vaccination Dashboard France

Un tableau de bord interactif d'analyse de la couverture vaccinale contre la COVID-19 en France, présentant une analyse comparative par territoire et démographie.

**[English version below](#english-version)**

## Objectif

Ce projet analyse l'équité de l'accès à la vaccination contre la COVID-19 en France en examinant les disparités géographiques et démographiques de la couverture vaccinale.

## Caractéristiques principales

- **Analyse Territoriale** : Visualisation géographique des taux de couverture par département
- **Analyse Démographique** : Comparaison des taux selon l'âge et le sexe
- **Mode Nuit/Jour** : Thème adaptable pour améliorer le confort de lecture
- **Multilingue** : Interface disponible en français et anglais
- **Data Storytelling** : Narration professionnelle des données

## Démarrage rapide

### Prérequis

- Python 3.10+
- pip ou conda

### Installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/nika14z/covid-vaccination-dashboard.git
   cd covid-vaccination-dashboard
   ```

2. **Créer un environnement virtuel** (optionnel mais recommandé)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Télécharger les données** (fichiers CSV)
   
   Les fichiers de données suivants doivent être placés dans le même répertoire que le script :
   - `vacsi-tot-a-dep-2023-07-13-15h50.csv` (données par âge et département)
   - `vacsi-tot-s-dep-2023-07-13-15h51.csv` (données par sexe et département)
   
   Sources : [data.gouv.fr - Santé Publique France](https://data.gouv.fr/)

5. **Lancer l'application**
   ```bash
   streamlit run app_streamlit.py
   ```

L'application s'ouvrira dans votre navigateur à `http://localhost:8501`

## Structure du projet

```
covid-vaccination-dashboard/
├── app_streamlit.py          # Application principale
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
└── data/                     # Dossier pour les données (non inclus)
    ├── vacsi-tot-a-dep-*.csv
    └── vacsi-tot-s-dep-*.csv
```

## 🔧 Fonctionnalités

### Pages principales

1. **Synthèse et Contexte**
   - Panorama national des taux de couverture
   - Contexte temporel et méthodologie
   - Informations sur la qualité des données

2. **Analyse Territoriale**
   - Carte interactive de France avec les taux par département
   - Classement des 20 meilleurs/pires départements
   - Indicateurs sélectionnables (Dose 1, Dose 2, Rappel, Rappel Bivalent)

3. **Analyse Démographique**
   - Couverture par groupe d'âge avec visualisations détaillées
   - Comparaison par sexe avec boxplots pour évaluer les disparités
   - Analyse de la distribution des vaccinations

### Options d'interface

- **Mode Nuit/Jour** : Toggle dans la barre latérale pour adapter les couleurs des graphiques
- **Langue** : Sélection Français/English dans les paramètres
- **Sélection dynamique** : Choix des indicateurs et des dimensions d'analyse

## 📊 Données

Les données proviennent de **Santé Publique France** via la plateforme [data.gouv.fr](https://data.gouv.fr/).

- **Format** : CSV
- **Périodicité** : Données à jour au 13 juillet 2023
- **Licence** : Licence Ouverte / Open Licence v2.0

### Variables disponibles

- Doses 1 et 2 (primo-vaccination)
- Doses de rappel
- Vaccin bivalent (Rappel adapté)
- Taux de couverture (%)
- Ventilation par groupe d'âge et sexe

## Technologies utilisées

- **[Streamlit](https://streamlit.io/)** - Framework web pour data apps
- **[Altair](https://altair-viz.github.io/)** - Visualisation de données déclarative
- **[Pandas](https://pandas.pydata.org/)** - Manipulation et analyse de données
- **[NumPy](https://numpy.org/)** - Calculs numériques

## Visualisations

- Cartes choroplèthes (Altair)
- Graphiques en barres et listes de classement
- Boîtes à moustaches (boxplots) pour les comparaisons d'inégalités
- Diagrammes en camembert pour la composition démographique
- Taux de couverture empilés avec pourcentages

##  Accessibilité

- Contraste suffisant en modes clair et sombre
- Labels clairs et lisibles sur tous les graphiques
- Interface responsive et multilingue
- Données et méthodologie documentées

## 👥 Auteurs

- **Nika Zarubina** - Auteur principal
  - [LinkedIn](https://www.linkedin.com/in/nika-zarubina-b5786593)
  
- **Mano Joseph Mathew** - Encadrant
  - [LinkedIn](https://www.linkedin.com/in/manomathew)

## Licence

Ce projet est fourni à titre de portfolio/exemple de visualisation de données.
Les données sont sous licence Ouverte v2.0.

## Problèmes et suggestions

Pour signaler un bug ou suggérer une amélioration, veuillez ouvrir une issue dans le repository GitHub.

---

## English Version

# COVID-19 Vaccination Dashboard France

An interactive dashboard analyzing COVID-19 vaccination coverage in France, with comparative analysis by territory and demographics.

## Objective

This project analyzes the equity of access to COVID-19 vaccination in France by examining geographic and demographic disparities in vaccination coverage.

## Quick Start

### Requirements

- Python 3.10+
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nika14z/covid-vaccination-dashboard.git
   cd covid-vaccination-dashboard
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download data files** (CSV format)
   
   Place the following data files in the same directory as the script:
   - `vacsi-tot-a-dep-2023-07-13-15h50.csv` (age and department data)
   - `vacsi-tot-s-dep-2023-07-13-15h51.csv` (gender and department data)
   
   Sources: [data.gouv.fr - Public Health France](https://data.gouv.fr/)

5. **Run the application**
   ```bash
   streamlit run app_streamlit.py
   ```

The app will open in your browser at `http://localhost:8501`

## Key Features

### Main Pages

1. **Summary & Context**
   - National vaccination coverage overview
   - Temporal context and methodology
   - Data quality information

2. **Territorial Analysis**
   - Interactive map of France with departmental rates
   - Ranking of top 20 departments
   - Selectable indicators (Dose 1, Dose 2, Booster, Bivalent Booster)

3. **Demographic Analysis**
   - Coverage by age group with detailed visualizations
   - Gender comparison with boxplots
   - Distribution analysis

## Technologies

- **[Streamlit](https://streamlit.io/)** - Web framework for data apps
- **[Altair](https://altair-viz.github.io/)** - Declarative data visualization
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[NumPy](https://numpy.org/)** - Numerical computing

## 📄 License

This project is provided as a portfolio/example of data visualization.
Data is under Open License v2.0.
