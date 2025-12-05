"""Application Streamlit - Tableau de bord Vaccination COVID-19 France.
Auteur : Nika ZARUBINA
Date : 2023
Description : Data Storytelling sur la vaccination (Pattern: Comparaison Régions/Groupes).
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from typing import Dict


# ============================================================================
# Configuration
# ============================================================================
st.set_page_config(
    page_title="COVID-19 Tracker France",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Constants ---
URL_GEOJSON = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
FILES = {
    "dep_age": "vacsi-tot-a-dep-2023-07-13-15h50.csv",
    "dep_sex": "vacsi-tot-s-dep-2023-07-13-15h51.csv",
}

# Colors used across charts
COLORS = {
    "dose_primary": "#3182bd",
    "dose_booster": "#31a354",
    "male": "#2171b5",
    "female": "#cb181d",
    "avg_line": "#e67e22",
    "gray_neutral": "#e0e0e0",
}

# Mapping des Âges (labels et ordre par défaut)
AGE_LABELS = {
    '0': '0-4 ans', '5': '5-9 ans', '10': '10-11 ans', '12': '12-17 ans',
    '18': '18-24 ans', '25': '25-29 ans', '30': '30-39 ans', '40': '40-49 ans',
    '50': '50-59 ans', '60': '60-64 ans', '65': '65-69 ans', '70': '70-74 ans',
    '75': '75-79 ans', '80': '80 ans et +'
}

AGE_ORDER = ['0-4 ans', '5-9 ans', '10-11 ans', '12-17 ans', '18-24 ans', '25-29 ans',
             '30-39 ans', '40-49 ans', '50-59 ans', '60-64 ans', '65-69 ans',
             '70-74 ans', '75-79 ans', '80 ans et +']



# Dictionnaire de traduction & Textes Narratifs
TRANSLATIONS = {
    'Français': {
        'nav_title': "Navigation",
        'nav_intro': "Synthèse et Contexte",
            'nav_geo': "Géographie",
            'nav_demo': "Démographie",
        'about': "Auteur",
        'prof': "Encadrant",
        'kpi_title': "Panorama National (Situation à date)",
        'intro_title': "Tableau de Bord Vaccination COVID-19",
        'intro_subtitle': "Analyse comparative de la couverture vaccinale par territoire et démographie",
        
        # NARRATIVE : HOOK & CONTEXT
        'tab_narrative': "Analyse et Synthèse",
        'tab_data': "Données et Méthodologie",
        'tab_quality': "Qualité",
        'intro_narrative_text': """
        ### Problématique Centrale
        La campagne de vaccination contre la COVID-19 en France a mobilisé des ressources massives sur tout le territoire.
        **Cependant, cette couverture a-t-elle été équitable pour tous les Français ?**

        ### Structure de l'Analyse
        Ce tableau de bord décompose cette question en deux dimensions complémentaires :
        
        **Dimension 1 : Variations Territoriales**  
        Certains départements ont-ils bénéficié d'une meilleure couverture que d'autres ? Existe-t-il des patterns régionaux ou une corrélation avec la densité de population ?
        
        **Dimension 2 : Variations Démographiques**  
        Comment la vaccination a-t-elle progressé selon l'âge et le sexe ? Quels groupes présentent les taux d'adhésion les plus élevés ou les plus faibles ?

        ### Contexte Temporel
        * **Janvier 2021 - Juin 2021** : Phase initiale (Doses 1 & 2, ciblage prioritaires)
        * **Juillet 2021** : Catalyseur majeur avec le Pass Sanitaire
        * **2022-2023** : Expansion vers les doses de rappel et vaccins adaptés
        """,
        
        'intro_data_text': "Données issues de **data.gouv.fr** (Santé Publique France).",
        'dq_limitations': "**Limitation technique :** Les taux > 100% (dus aux biais de recensement INSEE) sont plafonnés à 100% pour la lisibilité.",
        'dq_source': "**Source :** Santé Publique France (Fichiers VACSI)",
        'dq_license': "**Licence :** Licence Ouverte / Open Licence version 2.0",

            'geo_title': "Analyse Territoriale",
        'geo_desc': "Comparaison de la couverture vaccinale par département.",
        'geo_insight': "**Analyse :** On observe des disparités régionales significatives. Les départements urbains présentent des taux de couverture supérieurs à certains territoires moins denses.",
        'geo_implication': "**Interprétation :** Les zones à faible densité de population présentent des défis logistiques importants pour l'accès à la vaccination.",
        'geo_choose_dose': "Indicateur :",
        'geo_map_title': "Carte de France",
        'geo_rank_title': "Classement des départements",
        
            'demo_title': "Analyse Démographique",
        'demo_desc': "Couverture vaccinale par groupe d'âge et sexe.",
        'demo_insight_age': "**Analyse Âge :** Les groupes âgés (65+) présentent une couverture élevée (>90%), tandis que la couverture en doses de rappel diminue dans les groupes jeunes adultes.",
        'demo_implication_age': "**Interprétation :** Les stratégies de communication et d'accès doivent être adaptées aux caractéristiques sociodémographiques des différents groupes d'âge.",
        'demo_insight_sex': "**Analyse Sexe :** Les taux de couverture présentent une distribution similaire entre hommes et femmes, indiquant une adhésion équilibrée entre les sexes.",
        
        'demo_type_label': "Vue par :",
        'demo_type_age': "Âge",
        'demo_type_sex': "Sexe",
        'demo_choose_dose': "Stade vaccinal :",
        'prop_title': "Couverture par génération",
        'prop_vaccinated': "Vaccinés",
        'prop_non_vaccinated': "Non-vaccinés",
        'pie_title': "Poids démographique des vaccinés",
        'demo_boxplot_title': "Écarts de couverture (Dispersion)",
        'demo_boxplot_text': "Plus la boîte est grande, plus l'inégalité entre les départements est forte pour cet âge.",
        
        'tooltip_nat': "Moyenne Nationale",
        'axis_rate': "Taux (%)",
        'axis_dep': "Département",
        'axis_pop': "Population",
        'theme_label': "Mode Nuit",
        'cap_note': "Note : Les taux sont calculés par rapport à la population ciblée pour chaque stade vaccinal.",
        'tooltip_max': "Max",
        'tooltip_min': "Min",
        'tooltip_med': "Médiane",
        'axis_sex': "Sexe"
    },
    'English': {
        'nav_title': "Navigation",
        'nav_intro': "Summary & Context",
            'nav_geo': "Geography",
            'nav_demo': "Demographics",
        'about': "Author",
        'prof': "Supervisor",
        'kpi_title': "National Overview",
        'intro_title': "COVID-19 Vaccination Dashboard",
        'intro_subtitle': "Comparative analysis of vaccination coverage by territory and demographics",
        
        'tab_narrative': "Analysis & Summary",
        'tab_data': "Data & Methods",
        'tab_quality': "Quality",
        'intro_narrative_text': """
        ### Central Research Question
        The COVID-19 vaccination campaign in France mobilized massive resources across all territories.
        **However, was this coverage equitable for all citizens?**

        ### Analysis Structure
        This dashboard addresses this question across two complementary dimensions:
        
        **Dimension 1: Territorial Variations**  
        Did certain departments achieve better coverage than others? Are there regional patterns or correlations with population density?
        
        **Dimension 2: Demographic Variations**  
        How did vaccination progress according to age and gender? Which groups showed the highest or lowest uptake rates?

        ### Temporal Context
        * **January 2021 - June 2021**: Initial phase (Doses 1 & 2, targeting priority groups)
        * **July 2021**: Major catalyst with the Health Pass implementation
        * **2022-2023**: Expansion to booster doses and adapted vaccines
        """,
        
        'intro_data_text': "Data sourced from **data.gouv.fr** (Public Health France).",
        'dq_limitations': "**Technical Limit:** Rates > 100% (due to census bias) are capped at 100% for readability.",
        'dq_source': "**Source:** Public Health France (VACSI files)",
        'dq_license': "**License:** Open License version 2.0",
        
            'geo_title': "Territorial Analysis",
        'geo_desc': "Vaccination coverage comparison by department.",
        'geo_insight': "**Analysis:** Significant regional disparities are observed. Urban departments show higher coverage rates than some less densely populated territories.",
        'geo_implication': "**Interpretation:** Low-density population zones face substantial logistical challenges for vaccination access.",
        'geo_choose_dose': "Indicator:",
        'geo_map_title': "Map of France",
        'geo_rank_title': "Ranking by Department",
        
            'demo_title': "Demographic Analysis",
        'demo_desc': "Vaccination coverage by age group and gender.",
        'demo_insight_age': "**Age Analysis:** Older age groups (65+) show high coverage (>90%), while booster dose coverage decreases in younger adult cohorts.",
        'demo_implication_age': "**Interpretation:** Communication and access strategies must be adapted to the sociodemographic characteristics of different age groups.",
        'demo_insight_sex': "**Gender Analysis:** Coverage rates show similar distribution between men and women, indicating balanced uptake across genders.",
        
        'demo_type_label': "View by:",
        'demo_type_age': "Age",
        'demo_type_sex': "Gender",
        'demo_choose_dose': "Stage:",
        'prop_title': "Coverage by Generation",
        'prop_vaccinated': "Vaccinated",
        'prop_non_vaccinated': "Not Vaccinated",
        'pie_title': "Demographic weight of vaccinated",
        'demo_boxplot_title': "Coverage Gaps (Dispersion)",
        'demo_boxplot_text': "The wider the box, the higher the inequality between departments for this age group.",
        
        'tooltip_nat': "National Average",
        'axis_rate': "Rate (%)",
        'axis_dep': "Department",
        'axis_pop': "Population",
        'theme_label': "Night Mode",
        'cap_note': "Note: Rates are calculated relative to the target population for each vaccination stage.",
        'tooltip_max': "Max",
        'tooltip_min': "Min",
        'tooltip_med': "Median",
        'axis_sex': "Gender"
    }
}

# ==============================================================================
# 2. UTILS
# ==============================================================================

def fix_dep_code(c: any) -> str:
    c = str(c).strip()
    return "0" + c if len(c) == 1 else c

def apply_theme_css(dark_mode: bool):
    # CSS Custom pour les cartes KPI (Metrics)
    metric_card_css = """
<style>
div[data-testid="stMetric"] {
background-color: rgba(255, 255, 255, 0.05);
border: 1px solid rgba(255, 255, 255, 0.1);
padding: 10px;
border-radius: 5px;
text-align: center;
}
div[data-testid="stMetricLabel"] {
font-size: 0.9em;
opacity: 0.8;
}
div[data-testid="stMetricValue"] {
font-size: 1.6em;
font-weight: bold;
color: #5DADE2;
}
/* Style pour les Insights */
.insight-box {
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 20px;
    border-left: 5px solid #F39C12;
    background-color: rgba(243, 156, 18, 0.1);
}
</style>
"""
    if dark_mode:
        alt.themes.enable("dark")
        st.markdown("""<style>
            .stApp { background-color: #0E1117; }
            .stSidebar { background-color: #262730; }
            h1, h2, h3 { color: #FAFAFA !important; font-family: 'Segoe UI', sans-serif; }
            p, li, span, div { color: #E0E0E0; font-family: 'Segoe UI', sans-serif; }
        </style>""" + metric_card_css, unsafe_allow_html=True)
    else:
        alt.themes.enable("default")
        st.markdown("""
        <style>
            .stApp { background-color: #FFFFFF; }
            .stSidebar { background-color: #F8F9FA; border-right: 1px solid #ddd;}
            h1, h2, h3 { color: #111111 !important; font-family: 'Segoe UI', sans-serif; }
            p, li, span, div { color: #333333; font-family: 'Segoe UI', sans-serif; }
            .block-container { background: #fff !important; }
                header[data-testid="stHeader"] { background: #fff !important; }
        </style>
        """ + metric_card_css.replace("#5DADE2", "#3182bd"), unsafe_allow_html=True)

# ==============================================================================
# 3. LOAD DATA
# ==============================================================================

@st.cache_data
def load_dep_data(filepath):
    try:
        data = pd.read_csv(filepath, delimiter=';', dtype={'dep': str})
        data.columns = data.columns.str.lower()
        if 'jour' in data.columns: data = data[data['jour'] == data['jour'].max()]
        
        mapping = {
            'Dose 1': ['n_tot_dose1', 'n_cum_dose1'], 'Dose 2': ['n_tot_dose2', 'n_cum_dose2', 'n_tot_complet'],
            'Rappel 1': ['n_tot_rappel', 'n_cum_rappel'], 'Rappel 2': ['n_tot_2_rappel'],
            'Rappel 3': ['n_tot_3_rappel'], 'Rappel Bivalent': ['n_tot_rappel_biv']
        }
        
        cols_keep = ['dep', 'clage_vacsi', 'pop']
        rename = {'dep': 'Departement', 'clage_vacsi': 'Classe dAge', 'pop': 'Population'}
        found = []
        
        for n, opts in mapping.items():
            c = next((x for x in data.columns if x in opts), None)
            if c:
                cols_keep.append(c)
                rename[c] = n
                found.append(n)
                
        data = data[cols_keep].rename(columns=rename)
        data['Departement'] = data['Departement'].apply(fix_dep_code)
        data['Population'] = data['Population'].replace(0, np.nan)
        
        # NETTOYAGE ROBUSTE ET MAPPING DES AGES
        data['Classe dAge'] = pd.to_numeric(data['Classe dAge'], errors='coerce').astype('Int64').astype(str)
        data['Classe dAge'] = data['Classe dAge'].map(AGE_LABELS).fillna(data['Classe dAge'])
        
        for c in found:
            data[f"Taux {c} (%)"] = (data[c] / data['Population'] * 100).clip(upper=100)
            
        return data.replace([np.inf, np.nan], 0), found
    except Exception as e: 
        return None, []

@st.cache_data
def load_sex_data(filepath):
    try:
        data = pd.read_csv(filepath, delimiter=';', dtype={'dep': str})
        data.columns = data.columns.str.lower()
        if 'jour' in data.columns: data = data[data['jour'] == data['jour'].max()]
        if 'sexe' not in data.columns: return None
        
        data['sexe'] = data['sexe'].astype(str).str.replace('.0', '', regex=False)
        data = data[data['sexe'].isin(['1', '2'])]
        data['sexe'] = data['sexe'].map({'1': 'Homme', '2': 'Femme'})
        
        map_c = {
            'Dose 1': ['n_tot_dose1'], 'Dose 2': ['n_tot_dose2', 'n_tot_complet'],
            'Rappel 1': ['n_tot_rappel'], 'Rappel 2': ['n_tot_2_rappel'],
            'Rappel 3': ['n_tot_3_rappel'], 'Rappel Bivalent': ['n_tot_rappel_biv']
        }
        map_r = {
            'Dose 1': ['couv_tot_dose1'], 'Dose 2': ['couv_tot_complet'],
            'Rappel 1': ['couv_tot_rappel'], 'Rappel 2': ['couv_tot_2_rappel'],
            'Rappel 3': ['couv_tot_3_rappel'], 'Rappel Bivalent': ['couv_tot_rappel_biv']
        }
        
        cols, rename = ['dep', 'sexe'], {'dep': 'Departement', 'sexe': 'Sexe'}
        found_c, found_r = {}, {}
        
        for n, o in map_c.items():
            c = next((k for k in data.columns if k in o), None)
            if c:
                cols.append(c)
                rename[c] = n
                found_c[n] = n
        for n, o in map_r.items():
            c = next((k for k in data.columns if k in o), None)
            if c:
                cols.append(c)
                rename[c] = f"Taux {n} (%)"
                found_r[n] = f"Taux {n} (%)"
                
        data = data[cols].rename(columns=rename)
        data['Departement'] = data['Departement'].apply(fix_dep_code)
        
        if 'Dose 1' in found_c and 'Dose 1' in found_r:
            data['Population'] = np.where(data[found_r['Dose 1']] > 0, (data['Dose 1'] / data[found_r['Dose 1']]) * 100, 0).round().astype(int)
        else: data['Population'] = 1
        
        return data.replace([np.inf, np.nan], 0)
    except: return None

# ==============================================================================
# 4. VUES (PAGES)
# ==============================================================================

def page_introduction(df_dep, dict_fra, cols, lang):
    t = TRANSLATIONS[lang]
    
    # Hero Section avec gradient
    st.markdown("""
    <style>
        .hero-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            color: #666;
            font-style: italic;
            margin-bottom: 2rem;
        }
        .kpi-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(102, 126, 234, 0.05) 100%);
            border-left: 4px solid #667eea;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .kpi-label {
            font-size: 0.9rem;
            color: #666;
            margin: 0;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #667eea;
            margin: 0.5rem 0 0 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h1 class='hero-title'>{t['intro_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hero-subtitle'>{t['intro_subtitle']}</p>", unsafe_allow_html=True)
    
    if dict_fra:
        st.divider()
        st.subheader(t['kpi_title'])
        
        items = list(dict_fra.items())
        cols_display = st.columns(3)
        
        colors = ["#667eea", "#764ba2", "#f093fb"]
        for idx, (l, v) in enumerate(items):
            col_idx = idx % 3
            with cols_display[col_idx]:
                if l == "Rappel Biv.": l = "Rappel Bivalent"
                color = colors[col_idx]
                
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
                    border-left: 4px solid {color};
                    padding: 1.5rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                '>
                    <p style='font-size: 0.9rem; color: #666; margin: 0;'>{l}</p>
                    <p style='font-size: 1.8rem; font-weight: 700; color: {color}; margin: 0.5rem 0 0 0;'>{int(v):,}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
    
    # Tabs avec contenu
    t1, t2, t3 = st.tabs([t['tab_narrative'], t['tab_data'], t['tab_quality']])
    
    with t1:
        st.markdown(t['intro_narrative_text'])
    
    with t2:
        st.info(t['intro_data_text'])
        st.markdown(f"**Variables:** {', '.join(cols)}")
    
    with t3:
        st.warning(t['dq_limitations'])
        st.markdown(t['dq_source'])
        st.markdown(t['dq_license'])

def page_geo(df, cols, lang):
    t = TRANSLATIONS[lang]
    st.title(t['geo_title'])
    
    # determine theme for charts
    dark = st.session_state.get('dark', True)
    chart_bg = '#0E1117' if dark else '#ffffff'
    text_color = '#ffffff' if dark else '#111111'

    # Storytelling Block
    with st.container():
        st.info(t['geo_insight'])
        st.success(t['geo_implication'])
    
    st.markdown(t['geo_desc'])
    
    c1, c2 = st.columns([1, 2])
    with c1: dose = st.radio(t['geo_choose_dose'], cols)
    with c2: metric = st.radio("Métrique / Metric", ["Taux (%)" if lang=='Français' else "Rate (%)", "Total"])
    
    col_target = f"Taux {dose} (%)" if "Taux" in metric or "Rate" in metric else dose
    df_viz = df[df['Classe dAge'] == 'Tous âges'].copy()
    
    scheme = 'tealblues' if 'Rappel' in dose else 'yelloworangered'
    color_bar = COLORS['dose_booster'] if 'Rappel' in dose else COLORS['dose_primary']
    
    geo = alt.Data(url=URL_GEOJSON, format=alt.DataFormat(property='features', type='json'))
    sel = alt.selection_point(fields=['properties.nom'], on='mouseover', empty='none')
    
    map_c = alt.Chart(geo).mark_geoshape(stroke='white').encode(
        color=alt.Color(f'{col_target}:Q', scale=alt.Scale(scheme=scheme), legend=alt.Legend(title=t['axis_rate'])),
        opacity=alt.condition(sel, alt.value(1), alt.value(0.7)),
        tooltip=['properties.nom:N', alt.Tooltip(f'{col_target}:Q', format=',.1f')]
    ).transform_lookup(lookup='properties.code', from_=alt.LookupData(df_viz, 'Departement', [col_target])).add_params(sel).properties(width=600, height=500, background=chart_bg).project(type='identity', reflectY=True)
    
    # Configure legend labels for light mode on map
    if not dark:
        map_c = map_c.configure_legend(labelColor='#111111', titleColor='#111111')

    bar_c = alt.Chart(df_viz).mark_bar().encode(
        x=alt.X(col_target, title=""),
        y=alt.Y('Departement', sort='-x'),
        color=alt.condition(alt.datum[col_target] >= df_viz[col_target].mean(), alt.value(color_bar), alt.value('#BDC3C7')),
        tooltip=[col_target]
    ).transform_window(rank='rank()', sort=[alt.SortField(col_target, order='descending')]).transform_filter(alt.datum.rank <= 20).properties(height=500, title=f"Top 20 ({dose})", background=chart_bg)
    
    # Configure axis labels and title for light mode
    if not dark:
        bar_c = bar_c.configure_title(color='#111111').configure_axis(labelColor='#111111', titleColor='#111111').configure_legend(labelColor='#111111', titleColor='#111111')

    c_a, c_b = st.columns([1.5, 1])
    with c_a: st.altair_chart(map_c, use_container_width=True)
    with c_b: st.altair_chart(bar_c, use_container_width=True)

def page_demo(df_age, df_sex, cols, lang):
    t = TRANSLATIONS[lang]
    st.title(t['demo_title'])
    st.markdown(t['demo_desc'])

    # theme for charts
    dark = st.session_state.get('dark', True)
    chart_bg = '#0E1117' if dark else '#ffffff'
    text_color_name = 'white' if dark else 'black'  # CSS color names for Altair
    
    mode = st.radio(t['demo_type_label'], [t['demo_type_age'], t['demo_type_sex']], horizontal=True)
    st.markdown("---")
    
    # Storytelling Block
    with st.container():
        if mode == t['demo_type_age']:
            st.info(t['demo_insight_age'])
            st.success(t['demo_implication_age'])
        else:
            st.info(t['demo_insight_sex'])

    dose = st.radio(t['demo_choose_dose'], cols, horizontal=True, key="d")
    col_taux = f"Taux {dose} (%)"
    color = COLORS['dose_booster'] if 'Rappel' in dose else COLORS['dose_primary']
    
    if mode == t['demo_type_age']:
        df = df_age[df_age['Classe dAge'] != 'Tous âges'].copy()
        try: sort = [age for age in AGE_ORDER if age in df['Classe dAge'].unique()]
        except: sort = sorted(df['Classe dAge'].unique())
        
        st.subheader(t['prop_title'])
        agg = df.groupby('Classe dAge')[[dose, 'Population']].sum().reset_index()
        agg['V'] = agg[dose]; agg['NV'] = (agg['Population'] - agg['V']).clip(lower=0)
        melt = agg.melt('Classe dAge', ['V', 'NV'], 'S', 'C')
        melt['L'] = melt['S'].map({'V': t['prop_vaccinated'], 'NV': t['prop_non_vaccinated']})
        melt['P'] = melt['C'] / melt.groupby('Classe dAge')['C'].transform('sum')
        
        base = alt.Chart(melt).encode(x=alt.X('Classe dAge', sort=sort), y=alt.Y('C', stack="normalize", axis=alt.Axis(format='%')), order=alt.Order('S', sort='descending'))
        bars = base.mark_bar().encode(color=alt.Color('L', scale=alt.Scale(range=[color, COLORS['gray_neutral']]), legend=alt.Legend(title="Statut")))
        text = base.mark_text(dy=10, color=text_color_name).encode(text=alt.Text('P', format='.0%'), opacity=alt.condition(alt.datum.P > 0.05, alt.value(1), alt.value(0)))
        chart_combined = (bars + text).properties(height=350, background=chart_bg).interactive()
        if not dark:
            chart_combined = chart_combined.configure_axis(labelColor='#111111', titleColor='#111111').configure_legend(labelColor='#111111', titleColor='#111111')
        st.altair_chart(chart_combined, use_container_width=True)
        
        st.subheader(t['demo_boxplot_title'])
        st.markdown(f"*{t['demo_boxplot_text']}*")
        nat = df.groupby('Classe dAge')[[dose, 'Population']].sum().reset_index()
        nat['R'] = (nat[dose] / nat['Population'] * 100).clip(upper=100)
        
        box_base = alt.Chart(df).encode(x=alt.X('Classe dAge', sort=sort))
        box = box_base.mark_boxplot(extent='min-max', color=color).encode(y=alt.Y(col_taux))
        tick = alt.Chart(nat).mark_tick(color=COLORS['avg_line'], thickness=3, size=40).encode(x=alt.X('Classe dAge', sort=sort), y='R', tooltip=[alt.Tooltip('R', title=t['tooltip_nat'], format='.1f')])
        chart_boxplot = (box + tick).properties(background=chart_bg)
        if not dark:
            chart_boxplot = chart_boxplot.configure_axis(labelColor='#111111', titleColor='#111111')
        st.altair_chart(chart_boxplot, use_container_width=True)

    elif mode == t['demo_type_sex']:
        if df_sex is None: st.error("No Data")
        else:
            st.subheader("Comparaison Sexe")
            nat = df_sex.groupby('Sexe')[[dose, 'Population']].sum().reset_index()
            nat['R'] = (nat[dose] / nat['Population'] * 100).clip(upper=100)
            
            bar = alt.Chart(nat).mark_bar().encode(
                x=alt.X('Sexe', title=t['axis_sex']), y=alt.Y('R', title=t['axis_rate']),
                color=alt.Color('Sexe', scale=alt.Scale(range=[COLORS['male'], COLORS['female']])), tooltip=['Sexe', alt.Tooltip('R', format='.1f')]
            ).properties(height=300, background=chart_bg)
            if not dark:
                bar = bar.configure_axis(labelColor='#111111', titleColor='#111111').configure_legend(labelColor='#111111', titleColor='#111111')
            
            c1, c2 = st.columns([1, 2])
            with c1: st.altair_chart(bar, use_container_width=True)
            with c2:
                st.write("") 
                st.markdown(f"#### {t['demo_boxplot_title']}")
                base = alt.Chart(df_sex).encode(x=alt.X('Sexe', title=t['axis_sex']))
                box = base.mark_boxplot(extent='min-max', color=color).encode(y=alt.Y(col_taux, title=t['axis_rate']), tooltip=alt.value(None)).properties(background=chart_bg)
                if not dark:
                    box = box.configure_axis(labelColor='#111111', titleColor='#111111')
                
                # Tooltip personnalisé pour le sexe
                sel = base.mark_bar(opacity=0).encode(
                    y=alt.Y(col_taux, aggregate='max'), 
                    y2=alt.value(0),
                    tooltip=[
                        alt.Tooltip('Sexe', title=t['axis_sex']),
                        alt.Tooltip(col_taux, aggregate='max', title=t['tooltip_max'], format='.1f'),
                        alt.Tooltip(col_taux, aggregate='min', title=t['tooltip_min'], format='.1f'),
                        alt.Tooltip(col_taux, aggregate='median', title=t['tooltip_med'], format='.1f')
                    ]
                )
                st.altair_chart(box + sel, use_container_width=True)

    st.caption(t['cap_note'])

# ==============================================================================
# 5. MAIN
# ==============================================================================

def main():
    data_dep, cols = load_dep_data(FILES['dep_age'])
    data_sex = load_sex_data(FILES['dep_sex'])
    
    fra = {}
    if data_dep is not None:
        d = data_dep[data_dep['Classe dAge'] == 'Tous âges']
        dark = st.session_state.get('dark', True)
        fra = {c: d[c].sum() for c in cols if c in d.columns}
        
    if data_dep is None: st.stop()

    if 'lang' not in st.session_state: st.session_state.lang = 'Français'
    t = TRANSLATIONS[st.session_state.lang]

    with st.sidebar:
        st.markdown("""
        <style>
            .sidebar-min-author {
                font-size: 1rem;
                font-weight: 600;
                color: #3a8ee6;
                margin-bottom: 0.1rem;
                text-transform: none;
            }
            .sidebar-min-author a:hover {
                text-decoration: underline !important;
            }
            .sidebar-min-role {
                font-size: 0.92rem;
                color: #3a8ee6;
                margin-bottom: 0.5rem;
                text-transform: none;
            }
            .sidebar-min-role a:hover {
                text-decoration: underline !important;
            }
            .sidebar-min-title {
                font-size: 1.05rem;
                font-weight: 700;
                color: #3a5fc8;
                margin-bottom: 0.3rem;
                margin-top: 0.7rem;
                text-transform: none;
            }
            .sidebar-min-sep {
                border: none;
                border-top: 1px solid #e0e0e0;
                margin: 0.7rem 0 0.7rem 0;
            }
            .sidebar-min-settings {
                font-size: 0.93rem;
                color: #444;
                margin-top: 1.2rem;
                text-transform: none;
            }
            .stToggle label {
                color: #222 !important;
                font-size: 1rem;
                font-weight: 500;
                text-transform: none;
            }
        </style>
        """, unsafe_allow_html=True)
        # Auteur
        st.markdown("<div class='sidebar-min-title'>Auteur</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sidebar-min-author'><a href='https://www.linkedin.com/in/nika-zarubina-b5786593?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app' target='_blank' style='text-decoration: none; color: inherit;'>Nika Zarubina</a></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sidebar-min-role'>{t['prof']}: <a href='https://www.linkedin.com/in/manomathew?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app' target='_blank' style='text-decoration: none; color: inherit;'>Mano Joseph Mathew</a></div>", unsafe_allow_html=True)
        st.markdown("<hr class='sidebar-min-sep'>", unsafe_allow_html=True)
        # Navigation
        st.markdown("<div class='sidebar-min-title'>Navigation</div>", unsafe_allow_html=True)
        page = st.radio("Menu", [t['nav_intro'], t['nav_geo'], t['nav_demo']], label_visibility="collapsed")
        st.markdown("<hr class='sidebar-min-sep'>", unsafe_allow_html=True)
        # Paramètres
        st.markdown("<div class='sidebar-min-title'>Paramètres</div>", unsafe_allow_html=True)
        st.session_state.lang = st.radio("Langue", ["Français", "English"], label_visibility="collapsed")
        if 'dark' not in st.session_state:
            st.session_state['dark'] = True
        dark = st.checkbox(t['theme_label'], value=st.session_state.get('dark', True))
        st.session_state['dark'] = dark
        apply_theme_css(dark)

    if page == t['nav_intro']: page_introduction(data_dep, fra, cols, st.session_state.lang)
    elif page == t['nav_geo']: page_geo(data_dep, cols, st.session_state.lang)
    elif page == t['nav_demo']: page_demo(data_dep, data_sex, cols, st.session_state.lang)

if __name__ == "__main__":
    main()