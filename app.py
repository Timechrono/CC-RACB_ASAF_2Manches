# https://www.dropbox.com/scl/fi/hi24fjo0vbal4oiiwt9jl/logo-TimeC.png?rlkey=xlw0oqk9gdnq6v5dgahi0klg0&st=y86yrn6y&dl=1
import streamlit as st
import pandas as pd
import time
import requests
import io
import Essais

# ==============================================================================
# ⚠️ METTEZ VOTRE LIEN DROPBOX ICI (Assurez-vous qu'il se termine bien par dl=1)
# ==============================================================================
LIEN_DROPBOX_LOGO = "https://www.dropbox.com/scl/fi/hi24fjo0vbal4oiiwt9jl/logo-TimeC.png?rlkey=xlw0oqk9gdnq6v5dgahi0klg0&st=y86yrn6y&dl=1"

# --- DÉTECTION DES SCRIPTS DE COURSE DISPONIBLES ---
try:
    import Course_1_ASAF
    course1_disponible = True
except ModuleNotFoundError:
    course1_disponible = False

try:
    import Course_2_ASAF
    course2_disponible = True
except ModuleNotFoundError:
    course2_disponible = False

try:
    import Course_1_RACB
    course1_racb_disponible = True
except ModuleNotFoundError:
    course1_racb_disponible = False

try:
    import Course_2_RACB
    course2_racb_disponible = True
except ModuleNotFoundError:
    course2_racb_disponible = False

st.set_page_config(page_title="Live", layout="wide")

# --- CONCEPTION GRAPHIQUE GÉOMÉTRIQUE UNIFIÉE ---
st.markdown(f"""
<style>
[data-testid="stHeader"] {{ display: none !important; }}
button:focus, div:focus, input:focus, select:focus {{
    outline: none !important; border-color: transparent !important; box-shadow: none !important;
}}
.block-container {{ 
    padding-top: 5px !important; 
    padding-bottom: 0rem !important; 
    padding-left: 0.5rem !important; 
    padding-right: 0.5rem !important; 
}}
div[data-testid="stMainBlockContainer"] {{
    padding-top: 5px !important;
    margin-top: 0px !important;
}}
div[data-testid="stVerticalBlock"] {{
    gap: 0rem !important;
    padding-top: 0px !important;
}}
div.stElementContainer {{
    margin-top: 0px !important;
    margin-bottom: 0px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}}
.titre-live, .titre-hist, .titre-classement {{
    color: #FFFFFF !important; font-size: 1.05rem !important; font-weight: bold !important;
    padding: 4px 8px !important; border-radius: 3px !important;
    width: 100% !important; display: block !important; clear: both !important;
}}
.titre-live {{ background-color: #15803D !important; margin-top: 0px !important; margin-bottom: 6px !important; }}
.titre-hist {{ background-color: #475569 !important; margin-top: 25px !important; margin-bottom: 6px !important; }}
.titre-classement {{ background-color: #1E3A8A !important; margin-top: 0px !important; margin-bottom: 6px !important; }}

/* Style en gras sur la dernière colonne de l'historique */
.table-hist td:last-child {{ 
    font-weight: bold !important; 
    color: #0F172A !important; 
}}

/* Cadre vert très foncé, texte BLANC et NON GRAS pour le Refresh */
.refresh-bleu-clair-historique {{
    color: #FFFFFF !important;
    font-weight: normal !important;
    background-color: #064E3B !important;
    border: 1px solid #00FF00 !important;
    padding: 1px 6px !important;
    border-radius: 4px !important;
    display: inline-block !important;
    margin-left: 4px !important;
}}

.espace-classement-suivant {{
    margin-top: 25px !important;
}}

.table-responsive-container {{
    width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    margin-bottom: 10px !important;
}}

.table-compacte {{
    width: 100% !important; margin-bottom: 0px !important;
    border-collapse: collapse !important; table-layout: auto !important;
}}
.table-compacte tr {{ height: 18px !important; }}
.table-compacte th, .table-compacte td {{ 
    height: 18px !important; padding: 1px 5px !important; line-height: 1.1 !important; 
    font-size: 0.85rem !important; color: #000000 !important; vertical-align: middle !important; 
    white-space: nowrap !important; 
}}
.table-compacte td {{ border-bottom: 1px solid #E0E0E0 !important; background-color: #FFFFFF !important; }}
.table-compacte th {{ font-weight: bold !important; background-color: #F5F5F5 !important; border-bottom: 2px solid #CCCCCC !important; text-align: left !important; }}
.table-live td:last-child, .table-class-robuste td:last-child {{ font-weight: bold !important; font-size: 0.94rem !important; color: #0F172A !important; }}
.table-hist tr:nth-child(odd) td {{ background-color: #E0F2FE !important; }}

/* Signature alignée en bleu foncé avec pointillés assortis */
.signature-fin-page {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 12px !important;
    text-align: center !important;
    color: #1E3A8A !important;
    font-size: 0.92rem !important;
    font-weight: bold !important;
    padding-top: 8px !important;
    margin-top: 35px !important;
    border-top: 1px dashed #1E3A8A !important;
    width: 100% !important;
}}

.logo-signature {{
    height: 42px !important;
    width: auto !important;
    vertical-align: middle !important;
}}

@media (max-width: 768px) {{
    .block-container {{ padding-left: 2px !important; padding-right: 2px !important; }}
    .titre-live, .titre-hist, .titre-classement {{ font-size: 0.85rem !important; padding: 3px 6px !important; }}
    .table-compacte th, .table-compacte td {{ font-size: 0.65rem !important; padding: 1px 2px !important; }}
    
    /* Limite la colonne Groupe ou Gr/Div à 4 caractères max sur mobile */
    .table-hist td:nth-child(4) {{
        max-width: 32px !important;
        overflow: hidden !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
    }}
    
    /* MODIFICATION GLOBALE PRIORITAIRE SMARTPHONE : Limite la colonne Voiture (3e colonne) */
    .table-compacte td:nth-child(3), table td:nth-child(3) {{
        max-width: 60px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }}
    
    .table-live td:last-child, .table-class-robuste td:last-child {{ font-size: 0.70rem !important; }}
    .signature-fin-page {{ font-size: 0.75rem !important; padding-top: 4px !important; }}
    .logo-signature {{ height: 32px !important; }}
}}

/* Force la ligne bleue sur le BAS des cellules */
.table-class-robuste tr.ligne-bleue-separation td {{
    box-shadow: inset 0 -3px 0 0 #1E3A8A !important;
}}
/* Forçage de la ligne de séparation de classe ASAF */
tr.ligne-separation-classe td, .table-compacte tr.ligne-separation-classe td {{ 
    box-shadow: inset 0 -3px 0 0 #1E3A8A !important; 
}}
</style>
""", unsafe_allow_html=True)
def gen_html(df, cl):
    if isinstance(df, str): return df 
    if df is None or (isinstance(df, pd.DataFrame) and df.empty): 
        return f"<div class='table-responsive-container'><table class='table-compacte {cl}'><tr><td style='text-align: center; padding: 10px;'>Données indisponibles (Vérifiez Dropbox)</td></tr></table></div>"
    
    html_table = df.to_html(index=False, classes=f"table-compacte {cl}", escape=False, border=0)
    return f"<div class='table-responsive-container'>{html_table}</div>"

# --- LECTURE DU PARAMÈTRE DE COURSE DEPUIS L'URL ---
query_params = st.query_params
choix_course_url = query_params.get("course", "essais").lower()

if choix_course_url == "c1asaf" and course1_disponible:
    choix_course = "Course 1 ASAF"
elif choix_course_url == "c1racb" and course1_racb_disponible:
    choix_course = "Course 1 RACB"
elif choix_course_url == "c2asaf" and course2_disponible:
    choix_course = "Course 2 ASAF"
elif choix_course_url == "c2racb" and course2_racb_disponible:
    choix_course = "Course 2 RACB"
else:
    choix_course = "Essais"

d_liv, d_his, d_haut, d_milieu, d_bas = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
t_live, t_his, t_haut, t_milieu, t_bas = "Chronométrage", "Historique", "Classement Haut", "Classement Milieu", "Classement Bas"

try:
    from concurrent.futures import ThreadPoolExecutor

    def recuperer_avec_timeout():
        if choix_course == "Course 1 ASAF": return Course_1_ASAF.recuperer_donnees_course()
        elif choix_course == "Course 1 RACB": return Course_1_RACB.recuperer_donnees_course()
        elif choix_course == "Course 2 ASAF": return Course_2_ASAF.recuperer_donnees_course()
        elif choix_course == "Course 2 RACB": return Course_2_RACB.recuperer_donnees_course()
        else: return Essais.recuperer_donnees_course()

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(recuperer_avec_timeout)
        res = future.result(timeout=3.5)
        if res and len(res) == 10:
            d_liv, d_his, d_haut, d_milieu, d_bas, t_live, t_his, t_haut, t_milieu, t_bas = res
except Exception as e:
    t_live = "⚠️ Liaison Dropbox ralentie ou instable — Tentative de reconnexon en cours..."

# Ajustement forcé des largeurs de colonnes de l'Historique en mode Ordinateur
st.markdown("<style>@media (min-width: 769px) { .table-hist th:nth-child(1), .table-hist td:nth-child(1) { width: 8% !important; } .table-hist th:nth-child(2), .table-hist td:nth-child(2) { width: 32% !important; } .table-hist th:nth-child(3), .table-hist td:nth-child(3) { width: 28% !important; } .table-hist th:nth-child(4), .table-hist td:nth-child(4) { width: 10% !important; } .table-hist th:nth-child(5), .table-hist td:nth-child(5) { width: 5% !important; } .table-hist th:nth-child(6), .table-hist td:nth-child(6) { width: 17% !important; } }</style>", unsafe_allow_html=True)

cg, cd = st.columns([1.3, 0.9])
with cg:
    conteneur_titre_live = st.empty()
    st.markdown(gen_html(d_liv, "table-live"), unsafe_allow_html=True)
    if t_his: 
        st.markdown(f"<span class='titre-hist'>{t_his}</span>", unsafe_allow_html=True)
    st.markdown(gen_html(d_his, "table-hist"), unsafe_allow_html=True)
    
with cd:
    if choix_course != "Essais":
        if t_haut:
            st.markdown(f"<span class='titre-classement'>{t_haut}</span>", unsafe_allow_html=True)
            st.markdown(gen_html(d_haut, "table-class-robuste"), unsafe_allow_html=True)
        if t_milieu:
            st.markdown(f"<span class='titre-classement espace-classement-suivant'>{t_milieu}</span>", unsafe_allow_html=True)
            st.markdown(gen_html(d_milieu, "table-class-robuste"), unsafe_allow_html=True)
        if t_bas:
            st.markdown(f"<span class='titre-classement espace-classement-suivant'>{t_bas}</span>", unsafe_allow_html=True)
            st.markdown(gen_html(d_bas, "table-class-robuste"), unsafe_allow_html=True)
    else:
        if t_haut:
            st.markdown(f"<span class='titre-classement'>{t_haut}</span>", unsafe_allow_html=True)
            st.markdown(gen_html(d_bas, "table-class-robuste"), unsafe_allow_html=True)
        if t_milieu:
            st.markdown(f"<span class='titre-classement espace-classement-suivant'>{t_milieu}</span>", unsafe_allow_html=True)
            st.markdown(gen_html(d_haut, "table-class-robuste"), unsafe_allow_html=True)
        if t_bas:
            st.markdown(f"<span class='titre-classement espace-classement-suivant'>{t_bas}</span>", unsafe_allow_html=True)
            st.markdown(gen_html(d_milieu, "table-class-robuste"), unsafe_allow_html=True)

# Ligne de signature esthétique avec logo Dropbox
st.markdown(f"""
<div class='signature-fin-page'>
    <img src='{LIEN_DROPBOX_LOGO}' class='logo-signature'>
    www.timechrono.be
</div>
""", unsafe_allow_html=True)

# --- REFRESH ET DÉCOMPTE DYNAMIQUE SECONDE PAR SECONDE ---
for secondes_restantes in range(30, -1, -1):
    if "Derniers concurrents" in t_live or "DIRECT" in t_live.upper():
        conteneur_titre_live.markdown(f"<span class='titre-live'>🏎️ EN DIRECT / Derniers concurrents partis / <span class='refresh-bleu-clair-historique'>Refresh {secondes_restantes} Sec.</span></span>", unsafe_allow_html=True)
    else:
        conteneur_titre_live.markdown(f"<span class='titre-live'>{t_live}</span>", unsafe_allow_html=True)
    if secondes_restantes > 0:
        time.sleep(1)

st.rerun()
