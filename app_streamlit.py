"""Application Streamlit - Tableau de bord Vaccination COVID-19 France.
Auteur : Nika ZARUBINA
Date : 2023
Description : Data Storytelling sur la vaccination.
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os

# ============================================================================
# 1. Configuration (Doit être la toute première ligne)
# ============================================================================
st.set_page_config(
    page_title="COVID-19 Tracker France",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# 2. Gestion du Style (CSS)
# ============================================================================
def inject_custom_css(dark_mode: bool):
    """Injecte le CSS pour le thème et supprime la barre blanche."""
    
    # Couleurs dynamiques
    bg_color = "#0E1117" if dark_mode else "#FFFFFF"
    text_color = "#FAFAFA" if dark_mode else "#333333"
    card_bg = "rgba(255, 255, 255, 0.05)" if dark_mode else "rgba(0, 0, 0, 0.05)"
    sidebar_bg = "#262730" if dark_mode else "#F8F9FA"

    # CSS Global
    css = f"""
    <style>
        /* SUPPRESSION BARRE BLANCHE & HEADER */
        div[data-testid="stDecoration"] {{
            display: none;
        }}
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            margin-top: 0 !important;
        }}
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
            z-index: 1;
        }}

        /* THEME GLOBAL */
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        section[data-testid="stSidebar"] {{ background-color: {sidebar_bg}; }}
        
        /* TEXTES */
        h1, h2, h3, p, li, span, div {{
            font-family: 'Segoe UI', sans-serif;
            color: {text_color};
        }}
        
        /* SIDEBAR MINI */
        .sidebar-min-author {{ font-size: 1rem; font-weight: 600; color: #3a8ee6 !important; margin-bottom: 0.1rem; }}
        .sidebar-min-role {{ font-size: 0.92rem; color: #3a8ee6 !important; margin-bottom: 0.5rem; }}
        .sidebar-min-title {{ font-size: 1.05rem; font-weight: 700; color: #3a5fc8 !important; margin-top: 0.7rem; }}
        .sidebar-min-sep {{ border-top: 1px solid #e0e0e0; margin: 0.7rem 0; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    if dark_mode: alt.themes.enable("dark")
    else: alt.themes.enable("default")

# ============================================================================
# 3. Constantes & Mapping
# ============================================================================
URL_GEOJSON = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
FILES = {
    "dep_age": "vacsi-tot-a-dep-2023-07-13-15h50.csv",
    "dep_sex": "vacsi-tot-s-dep-2023-07-13-15h51.csv",
}

COLORS = {
    "dose_primary": "#3182bd", "dose_booster": "#31a354",
    "male": "#2171b5", "female": "#cb181d",
    "avg_line": "#e67e22", "gray_neutral": "#e0e0e0",
}

AGE_MAPPING = {
    0: 'Tous âges', 4: '0-4 ans', 9: '5-9 ans', 11: '10-11 ans', 17: '12-17 ans',
    24: '18-24 ans', 29: '25-29 ans', 39: '30-39 ans', 49: '40-49 ans',
    59: '50-59 ans', 64: '60-64 ans', 69: '65-69 ans', 74: '70-74 ans',
    79: '75-79 ans', 80: '80 ans et +'
}
AGE_ORDER = ['Tous âges', '0-4 ans', '5-9 ans', '10-11 ans', '12-17 ans', '18-24 ans', '25-29 ans',
             '30-39 ans', '40-49 ans', '50-59 ans', '60-64 ans', '65-69 ans',
             '70-74 ans', '75-79 ans', '80 ans et +']

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
        
        'tab_narrative': "Analyse et Synthèse",
        'tab_data': "Données et Méthodologie",
        'tab_quality': "Qualité",
        'intro_narrative_text': """
        ### Problématique Centrale
        La campagne de vaccination contre la COVID-19 en France a mobilisé des ressources massives sur tout le territoire.
        **Cependant, cette couverture a-t-elle été équitable pour tous les Français ?**

        ### Structure de l'Analyse
        Ce tableau de bord décompose cette question en deux dimensions complémentaires :
        
        **Dimension 1 : Variations Territoriales** Certains départements ont-ils bénéficié d'une meilleure couverture que d'autres ? Existe-t-il des patterns régionaux ou une corrélation avec la densité de population ?
        
        **Dimension 2 : Variations Démographiques** Comment la vaccination a-t-elle progressé selon l'âge et le sexe ? Quels groupes présentent les taux d'adhésion les plus élevés ou les plus faibles ?

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
        
        **Dimension 1: Territorial Variations** Did certain departments achieve better coverage than others? Are there regional patterns or correlations with population density?
        
        **Dimension 2: Demographic Variations** How did vaccination progress according to age and gender? Which groups showed the highest or lowest uptake rates?

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
# 4. Chargement des Données
# ==============================================================================
def fix_dep_code(c: any) -> str:
    c = str(c).strip()
    return "0" + c if len(c) == 1 else c

@st.cache_data
def load_dep_data(filepath):
    if not os.path.exists(filepath):
        st.error(f"Fichier introuvable: {filepath}")
        return None, []
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
        rename = {'dep': 'Departement', 'clage_vacsi': 'CodeAge', 'pop': 'Population'}
        found = []
        for n, opts in mapping.items():
            c = next((x for x in data.columns if x in opts), None)
            if c:
                cols_keep.append(c); rename[c] = n; found.append(n)
                
        data = data[cols_keep].rename(columns=rename)
        data['Departement'] = data['Departement'].apply(fix_dep_code)
        data['Population'] = data['Population'].replace(0, np.nan)
        
        # MAPPING CORRIGÉ
        data['CodeAge'] = pd.to_numeric(data['CodeAge'], errors='coerce').fillna(-1).astype(int)
        data['Classe dAge'] = data['CodeAge'].map(AGE_MAPPING)
        data = data.dropna(subset=['Classe dAge'])
        
        for c in found:
            data[f"Taux {c} (%)"] = (data[c] / data['Population'] * 100).clip(upper=100)
        return data.replace([np.inf, np.nan], 0), found
    except Exception as e:
        st.error(f"Erreur Load Data: {e}"); return None, []

@st.cache_data
def load_sex_data(filepath):
    if not os.path.exists(filepath): return None
    try:
        data = pd.read_csv(filepath, delimiter=';', dtype={'dep': str})
        data.columns = data.columns.str.lower()
        if 'jour' in data.columns: data = data[data['jour'] == data['jour'].max()]
        if 'sexe' not in data.columns: return None
        data['sexe'] = data['sexe'].astype(str).str.replace('.0', '', regex=False)
        data = data[data['sexe'].isin(['1', '2'])]
        data['sexe'] = data['sexe'].map({'1': 'Homme', '2': 'Femme'})
        
        map_c = {'Dose 1': ['n_tot_dose1'], 'Dose 2': ['n_tot_dose2'], 'Rappel 1': ['n_tot_rappel'], 'Rappel 2': ['n_tot_2_rappel']}
        map_r = {'Dose 1': ['couv_tot_dose1'], 'Dose 2': ['couv_tot_complet'], 'Rappel 1': ['couv_tot_rappel'], 'Rappel 2': ['couv_tot_2_rappel']}
        
        cols, rename = ['dep', 'sexe'], {'dep': 'Departement', 'sexe': 'Sexe'}
        found_c, found_r = {}, {}
        for n, o in map_c.items():
            c = next((k for k in data.columns if k in o), None)
            if c: cols.append(c); rename[c] = n; found_c[n] = n
        for n, o in map_r.items():
            c = next((k for k in data.columns if k in o), None)
            if c: cols.append(c); rename[c] = f"Taux {n} (%)"; found_r[n] = f"Taux {n} (%)"
                
        data = data[cols].rename(columns=rename)
        data['Departement'] = data['Departement'].apply(fix_dep_code)
        if 'Dose 1' in found_c and 'Dose 1' in found_r:
            data['Population'] = np.where(data[found_r['Dose 1']] > 0, (data['Dose 1'] / data[found_r['Dose 1']]) * 100, 0).round().astype(int)
        else: data['Population'] = 1
        return data.replace([np.inf, np.nan], 0)
    except: return None

# ==============================================================================
# 5. Vues (AVEC LE DESIGN ORIGINAL RESTAURÉ)
# ==============================================================================
def page_introduction(df_dep, dict_fra, cols, lang):
    t = TRANSLATIONS[lang]
    
    # RESTAURATION DU CSS SPÉCIFIQUE À LA PAGE D'ACCUEIL
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
            color: #888888;
            font-style: italic;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<h1 class='hero-title'>{t['intro_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hero-subtitle'>{t['intro_subtitle']}</p>", unsafe_allow_html=True)
    
    if dict_fra:
        st.divider()
        st.subheader(t['kpi_title'])
        items = list(dict_fra.items())
        
        kpi_cols = st.columns(3)
        colors = ["#667eea", "#764ba2", "#f093fb"]
        
        for idx, (l, v) in enumerate(items):
            if idx < 3:
                with kpi_cols[idx]:
                    if l == "Rappel Biv.": l = "Rappel Bivalent"
                    color = colors[idx % 3]
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
                        border-left: 4px solid {color}; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                        <p style='font-size: 0.9rem; margin: 0; opacity: 0.8;'>{l}</p>
                        <p style='font-size: 1.8rem; font-weight: 700; color: {color}; margin: 0.5rem 0 0 0;'>{int(v):,}</p>
                    </div>""", unsafe_allow_html=True)
        st.divider()
    
    t1, t2, t3 = st.tabs([t['tab_narrative'], t['tab_data'], t['tab_quality']])
    with t1: st.markdown(t['intro_narrative_text'])
    with t2:
        st.info(t['intro_data_text'])
        st.markdown(f"**Variables:** {', '.join(cols)}")
    with t3: st.warning(t['dq_limitations']); st.markdown(t['dq_source']); st.markdown(t['dq_license'])

def page_geo(df, cols, lang):
    t = TRANSLATIONS[lang]
    st.title(t['geo_title'])
    dark = st.session_state.get('dark', True)
    chart_bg = '#0E1117' if dark else '#ffffff'
    
    with st.container(): st.info(t['geo_insight']); st.success(t['geo_implication'])
    st.markdown(t['geo_desc'])
    
    c1, c2 = st.columns([1, 2])
    with c1: dose = st.radio(t['geo_choose_dose'], cols)
    with c2: metric = st.radio("Métrique", ["Taux (%)", "Total"] if lang=='Français' else ["Rate (%)", "Total"])
    col_target = f"Taux {dose} (%)" if "Taux" in metric or "Rate" in metric else dose
    
    df_viz = df[df['Classe dAge'] == 'Tous âges'].copy()
    if df_viz.empty: st.error("Mapping 'Tous âges' vide."); return
    
    scheme = 'tealblues' if 'Rappel' in dose else 'yelloworangered'
    color_bar = COLORS['dose_booster'] if 'Rappel' in dose else COLORS['dose_primary']
    
    geo = alt.Data(url=URL_GEOJSON, format=alt.DataFormat(property='features', type='json'))
    sel = alt.selection_point(fields=['properties.nom'], on='mouseover', empty='none')
    
    map_c = alt.Chart(geo).mark_geoshape(stroke='white', strokeWidth=0.5).encode(
        color=alt.Color(f'{col_target}:Q', scale=alt.Scale(scheme=scheme), legend=alt.Legend(title=t['axis_rate'])),
        opacity=alt.condition(sel, alt.value(1), alt.value(0.7)),
        tooltip=['properties.nom:N', alt.Tooltip(f'{col_target}:Q', format=',.1f')]
    ).transform_lookup(lookup='properties.code', from_=alt.LookupData(df_viz, 'Departement', [col_target])).add_params(sel).properties(width=600, height=500, background=chart_bg).project(type='identity', reflectY=True)
    
    bar_c = alt.Chart(df_viz).mark_bar().encode(
        x=alt.X(col_target, title=""), y=alt.Y('Departement', sort='-x'),
        color=alt.condition(alt.datum[col_target] >= df_viz[col_target].mean(), alt.value(color_bar), alt.value('#BDC3C7')),
        tooltip=[col_target]
    ).transform_window(rank='rank()', sort=[alt.SortField(col_target, order='descending')]).transform_filter(alt.datum.rank <= 20).properties(height=500, title=f"Top 20 ({dose})", background=chart_bg)
    
    if not dark:
        map_c = map_c.configure_legend(labelColor='#333', titleColor='#333')
        bar_c = bar_c.configure_axis(labelColor='#333', titleColor='#333').configure_title(color='#333')
    
    c_a, c_b = st.columns([1.5, 1])
    with c_a: st.altair_chart(map_c, use_container_width=True)
    with c_b: st.altair_chart(bar_c, use_container_width=True)

def page_demo(df_age, df_sex, cols, lang):
    t = TRANSLATIONS[lang]
    st.title(t['demo_title'])
    st.markdown(t['demo_desc'])
    dark = st.session_state.get('dark', True)
    chart_bg = '#0E1117' if dark else '#ffffff'
    txt_col = 'white' if dark else 'black'
    
    mode = st.radio(t['demo_type_label'], [t['demo_type_age'], t['demo_type_sex']], horizontal=True)
    st.markdown("---")
    
    with st.container():
        if mode == t['demo_type_age']: st.info(t['demo_insight_age']); st.success(t['demo_implication_age'])
        else: st.info(t['demo_insight_sex'])
            
    dose = st.radio(t['demo_choose_dose'], cols, horizontal=True, key="d")
    col_taux = f"Taux {dose} (%)"
    color = COLORS['dose_booster'] if 'Rappel' in dose else COLORS['dose_primary']
    
    if mode == t['demo_type_age']:
        df = df_age[df_age['Classe dAge'] != 'Tous âges'].copy()
        sort_order = [age for age in AGE_ORDER if age in df['Classe dAge'].unique()]
        
        st.subheader(t['prop_title'])
        agg = df.groupby('Classe dAge')[[dose, 'Population']].sum().reset_index()
        agg['V'] = agg[dose]; agg['NV'] = (agg['Population'] - agg['V']).clip(lower=0)
        melt = agg.melt('Classe dAge', ['V', 'NV'], 'S', 'C')
        melt['L'] = melt['S'].map({'V': t['prop_vaccinated'], 'NV': t['prop_non_vaccinated']})
        melt['P'] = melt['C'] / melt.groupby('Classe dAge')['C'].transform('sum')
        
        base = alt.Chart(melt).encode(x=alt.X('Classe dAge', sort=sort_order), y=alt.Y('C', stack="normalize", axis=alt.Axis(format='%')), order=alt.Order('S', sort='descending'))
        bars = base.mark_bar().encode(color=alt.Color('L', scale=alt.Scale(range=[color, COLORS['gray_neutral']]), legend=alt.Legend(title="Statut")))
        text = base.mark_text(dy=10, color=txt_col).encode(text=alt.Text('P', format='.0%'), opacity=alt.condition(alt.datum.P > 0.05, alt.value(1), alt.value(0)))
        chart_comb = (bars + text).properties(height=350, background=chart_bg).interactive()
        if not dark: chart_comb = chart_comb.configure_axis(labelColor='#333', titleColor='#333').configure_legend(labelColor='#333', titleColor='#333')
        st.altair_chart(chart_comb, use_container_width=True)
        
        st.subheader(t['demo_boxplot_title'])
        st.caption(t['demo_boxplot_text'])
        nat = df.groupby('Classe dAge')[[dose, 'Population']].sum().reset_index()
        nat['R'] = (nat[dose] / nat['Population'] * 100).clip(upper=100)
        
        # FIX ALTAIR: properties() appliqué APRÈS l'addition
        box = alt.Chart(df).mark_boxplot(extent='min-max', color=color).encode(x=alt.X('Classe dAge', sort=sort_order), y=alt.Y(col_taux))
        tick = alt.Chart(nat).mark_tick(color=COLORS['avg_line'], thickness=3, size=40).encode(x=alt.X('Classe dAge', sort=sort_order), y='R')
        
        final_chart = (box + tick).properties(background=chart_bg)
        if not dark: final_chart = final_chart.configure_axis(labelColor='#333', titleColor='#333')
        st.altair_chart(final_chart, use_container_width=True)
        
    elif mode == t['demo_type_sex']:
        if df_sex is None: st.error("Données Sexe non disponibles")
        else:
            nat = df_sex.groupby('Sexe')[[dose, 'Population']].sum().reset_index()
            nat['R'] = (nat[dose] / nat['Population'] * 100).clip(upper=100)
            bar = alt.Chart(nat).mark_bar().encode(
                x=alt.X('Sexe', title=t['axis_sex']), y=alt.Y('R', title=t['axis_rate']),
                color=alt.Color('Sexe', scale=alt.Scale(range=[COLORS['male'], COLORS['female']])),
                tooltip=['Sexe', alt.Tooltip('R', format='.1f')]
            ).properties(height=300, background=chart_bg)
            
            c1, c2 = st.columns([1, 2])
            with c1: st.altair_chart(bar, use_container_width=True)
            with c2:
                st.markdown(f"#### {t['demo_boxplot_title']}")
                
                # FIX ALTAIR: properties() appliqué APRÈS l'addition
                base = alt.Chart(df_sex).encode(x=alt.X('Sexe', title=t['axis_sex']))
                box = base.mark_boxplot(extent='min-max', color=color).encode(y=alt.Y(col_taux, title=t['axis_rate']))
                
                sel = base.mark_bar(opacity=0).encode(
                    y=alt.Y(col_taux, aggregate='max'), y2=alt.value(0),
                    tooltip=[
                        alt.Tooltip('Sexe', title=t['axis_sex']),
                        alt.Tooltip(col_taux, aggregate='max', title=t['tooltip_max']),
                        alt.Tooltip(col_taux, aggregate='min', title=t['tooltip_min']),
                        alt.Tooltip(col_taux, aggregate='median', title=t['tooltip_med'])
                    ]
                )
                
                final_chart = (box + sel).properties(background=chart_bg)
                if not dark: final_chart = final_chart.configure_axis(labelColor='#333', titleColor='#333')
                st.altair_chart(final_chart, use_container_width=True)
    st.caption(t['cap_note'])

# ==============================================================================
# 6. MAIN
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("""<style>.sidebar-min-author{font-size:1rem;font-weight:600;color:#3a8ee6;margin-bottom:0.1rem}.sidebar-min-role{font-size:0.92rem;color:#3a8ee6;margin-bottom:0.5rem}.sidebar-min-title{font-size:1.05rem;font-weight:700;color:#3a5fc8;margin-top:0.7rem}.sidebar-min-sep{border-top:1px solid #e0e0e0;margin:0.7rem 0}</style>""", unsafe_allow_html=True)
        st.header("Paramètres")
        lang_select = st.radio("Langue", ["Français", "English"], key="lang")
        dark_mode = st.toggle("Mode Nuit", value=True, key="dark")
        inject_custom_css(dark_mode)
        
        st.markdown("<hr class='sidebar-min-sep'>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-min-title'>Navigation</div>", unsafe_allow_html=True)
        t_temp = TRANSLATIONS[lang_select]
        menu_options = [t_temp['nav_intro'], t_temp['nav_geo'], t_temp['nav_demo']]
        page = st.radio("Menu", menu_options, label_visibility="collapsed")
        
        st.divider()
        # AJOUT DES LIENS CLIQUABLES ICI
        st.markdown(f"""
        <div class='sidebar-min-author'>
            Auteur: <a href='https://www.linkedin.com/in/nika-zarubina-b5786593' target='_blank' style='text-decoration: none; color: inherit;'>Nika Zarubina</a>
        </div>
        <div class='sidebar-min-role'>
            {t_temp['prof']}: <a href='https://www.linkedin.com/in/manomathew' target='_blank' style='text-decoration: none; color: inherit;'>Mano J. Mathew</a>
        </div>
        """, unsafe_allow_html=True)

    data_dep, cols = load_dep_data(FILES['dep_age'])
    data_sex = load_sex_data(FILES['dep_sex'])
    fra = {}
    if data_dep is not None:
        d = data_dep[data_dep['Classe dAge'] == 'Tous âges']
        fra = {c: d[c].sum() for c in cols if c in d.columns}

    if data_dep is None: st.stop()
    t = TRANSLATIONS[st.session_state.lang]

    if page == t['nav_intro']: page_introduction(data_dep, fra, cols, st.session_state.lang)
    elif page == t['nav_geo']: page_geo(data_dep, cols, st.session_state.lang)
    elif page == t['nav_demo']: page_demo(data_dep, data_sex, cols, st.session_state.lang)

if __name__ == "__main__":
    if 'lang' not in st.session_state: st.session_state.lang = 'Français'
    if 'dark' not in st.session_state: st.session_state.dark = True
    main()