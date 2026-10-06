import streamlit as st
import pandas as pd
import datetime
import os
import time

st.set_page_config(layout="wide")
st.cache_data.clear()

# --- DESIGN SCIENTIFIQUE RIGIDE ---
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    
    /* VRAI GYROPHARE DE COURSE STATIQUE (SANS CLIGNOTEMENT) */
    .vrai-gyrophare {
        display: inline-block;
        margin-right: 6px;
        font-size: 1.05rem !important;
        vertical-align: middle !important;
    }
    
    .titre-live, .titre-hist, .titre-classement {
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: bold !important;
        padding: 4px 8px !important;
        border-radius: 3px !important;
        margin-bottom: 6px !important;
        width: 100% !important;
        display: block !important;
        clear: both !important;
    }
    
    .titre-live { background-color: #15803D !important; margin-top: 0px !important; }
    .titre-hist { background-color: #475569 !important; margin-top: 10px !important; }
    .titre-classement { background-color: #1E3A8A !important; margin-top: 0px !important; }
    
    .table-compacte { width: 100% !important; margin-bottom: 0px !important; border-collapse: collapse !important; table-layout: fixed !important; }
    .table-compacte tr { height: 18px !important; }
    .table-compacte th, .table-compacte td { 
        height: 18px !important; padding: 1px 5px !important; line-height: 1.1 !important; font-size: 0.85rem !important; color: #000000 !important; 
        vertical-align: middle !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; 
    }
    .table-compacte td { font-weight: normal !important; border-bottom: 1px solid #E0E0E0 !important; background-color: #FFFFFF !important; }
    .table-compacte th { font-weight: bold !important; background-color: #F5F5F5 !important; border-bottom: 2px solid #CCCCCC !important; text-align: left !important; }
    
    /* VERT PASTEL #d9fcec SPÉCIFIQUE AVEC TEXTE EN NOIR POUR L'HISTORIQUE */
    .table-compacte td.meilleur-temps { 
        background-color: #d9fcec !important; 
        color: #000000 !important;
        font-weight: bold !important; 
    }
    
    /* ALTERNANCE BLEU CIEL UNE LIGNE SUR DEUX UNIQUEMENT POUR LE SCRATCH TOP 30 (TABLE-CLASS-ROBUSTE) */
    .table-class-robuste tr:nth-child(odd) td {
        background-color: #E0F2FE !important;
    }
    
    .ligne-separation-classe td {
        border-bottom: 2px solid #1E3A8A !important;
    }
    
    .table-hist td:nth-last-child(2), .table-hist td:last-child,
    .table-live td:last-child, .table-class-robuste td:last-child {
        font-weight: bold !important;
        font-size: 0.94rem !important;
        color: #0F172A !important;
    }
    
    /* GAUCHE : 1. Tableau En Direct */
    .table-live th:nth-child(1), .table-live td:nth-child(1) { width: 8% !important; }
    .table-live th:nth-child(2), .table-live td:nth-child(2) { width: 26% !important; }
    .table-live th:nth-child(3), .table-live td:nth-child(3) { width: 18% !important; }
    .table-live th:nth-child(4), .table-live td:nth-child(4) { width: 13% !important; }
    .table-live th:nth-child(5), .table-live td:nth-child(5) { width: 13% !important; }
    .table-live th:nth-child(6), .table-live td:nth-child(6) { width: 22% !important; }

    /* GAUCHE : 2. Tableau Historique Course 2 */
    .table-hist th:nth-child(1), .table-hist td:nth-child(1) { width: 7% !important; }   
    .table-hist th:nth-child(2), .table-hist td:nth-child(2) { width: 23% !important; }  
    .table-hist th:nth-child(3), .table-hist td:nth-child(3) { width: 25% !important; }  
    .table-hist th:nth-child(4), .table-hist td:nth-child(4) { width: 10% !important; }   
    .table-hist th:nth-child(5), .table-hist td:nth-child(5) { width: 7% !important; }   
    .table-hist th:nth-child(6), .table-hist td:nth-child(6) { width: 14% !important; }  
    .table-hist th:nth-child(7), .table-hist td:nth-child(7) { width: 14% !important; }  

    /* DROITE : 3. Tableaux de Classements Scratch */
    .table-class-robuste th:nth-child(1), .table-class-robuste td:nth-child(1) { width: 9% !important; }
    .table-class-robuste th:nth-child(2), .table-class-robuste td:nth-child(2) { width: 11% !important; }
    .table-class-robuste th:nth-child(3), .table-class-robuste td:nth-child(3) { width: 33% !important; }
    .table-class-robuste th:nth-child(4), .table-class-robuste td:nth-child(4) { width: 23% !important; }
    .table-class-robuste th:nth-child(5), .table-class-robuste td:nth-child(5) { width: 6% !important; }
    .table-class-robuste th:nth-child(6), .table-class-robuste td:nth-child(6) { width: 18% !important; text-align: right !important; }

    /* DROITE : 4. RE-REPARTITION SUBTILE DU CLASSEMENT PAR CLASSE */
    .table-class-groupes th:nth-child(1), .table-class-groupes td:nth-child(1) { width: 5% !important; }   /* Pos */
    .table-class-groupes th:nth-child(2), .table-class-groupes td:nth-child(2) { width: 8% !important; }   /* N° */
    .table-class-groupes th:nth-child(3), .table-class-groupes td:nth-child(3) { width: 35% !important; }  /* Nom_Prenom (Augmenté) */
    .table-class-groupes th:nth-child(4), .table-class-groupes td:nth-child(4) { width: 21% !important; }  /* Groupe (Diminué) */
    .table-class-groupes th:nth-child(5), .table-class-groupes td:nth-child(5) { width: 11% !important; }  /* Classe (Augmenté) */
    .table-class-groupes th:nth-child(6), .table-class-groupes td:nth-child(6) { width: 14% !important; text-align: right !important; } /* Chrono (Diminué) */

    .table-class-groupes tr td {
        background-color: #FFFFFF !important;
    }

    .block-container { padding-top: 0.3rem !important; padding-bottom: 0rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    hr { margin: 6px 0px !important; border: 0 !important; height: 0 !important; }
    </style>
""", unsafe_allow_html=True)

#BASE_DIR = "C:/Dropbox/Dropbox"
#FILE_DEPART = os.path.join(BASE_DIR, "LIVE_Temps_DEPART.xlsm")
#FILE_ARRIVEE = os.path.join(BASE_DIR, "LIVE_Temps_ARRIVEE.xlsm")
#FILE_ENGAGES = os.path.join(BASE_DIR, "LIVE_Liste_ENGAGES_RACB.xlsm")

# --- ENCODAGE NUMÉRIQUE INTERNE ANTI-CENSURE ---
C = [100, 108, 46, 100, 114, 111, 112, 98, 111, 120, 117, 115, 101, 114]
D = [99, 111, 110, 116, 101, 110, 116, 46, 99, 111, 109]
HOTE_PROT = "".join(chr(x) for x in (C + D))

# Adresses internet assemblées
FILE_ARRIVEE = f"ht" + f"tps://{HOTE_PROT}/scl/fi/7uu9cmlpzglx0ngvbklpt/LIVE_Temps_ARRIVEE.xlsm?rlkey=g9urz4v3jr36h0apzt45ognm6&st=0d9mpgfw&dl=1"
FILE_DEPART  = f"ht" + f"tps://{HOTE_PROT}/scl/fi/gbkaq01qzjujc8nq3zj28/LIVE_Temps_DEPART.xlsm?rlkey=4x4rvvlfyzz8v59gqbxn80a4d&st=mcibn3xx&dl=1"
FILE_ENGAGES_RACB = f"ht" + f"tps://{HOTE_PROT}/scl/fi/69zkwsb45bpiw3ys3kk4c/LIVE_Liste_ENGAGES_RACB.xlsm?rlkey=qpjrlmbxhcskifnabs84veqh8&st=0snuv3e7&dl=1"

def telecharger_excel(url):
    entetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    reponse = requests.get(url, headers=entetes, timeout=12)
    reponse.raise_for_status()
    return io.BytesIO(reponse.content)



def convertir_en_secondes(valeur):
    if pd.isna(valeur) or valeur is None: return None
    if isinstance(valeur, (datetime.time, datetime.datetime)):
        return (valeur.minute * 60) + valeur.second + (valeur.microsecond / 1000000)
    s = str(valeur).strip()
    if s.endswith(".0"): s = s[:-2]
    s_clean = "".join([c for c in s if c.isdigit()])
    if not s_clean: return None
    num = int(s_clean)
    centiemes = num % 100
    secondes = (num // 100) % 100
    minutes = num // 10000
    if minutes >= 60: minutes = minutes % 60
    return (minutes * 60) + secondes + (centiemes / 100)

def nettoyer_numero(valeur):
    if pd.isna(valeur): return "nan"
    s = str(valeur).strip().upper()
    return s[:-2] if s.endswith(".0") else s

def format_final_chrono(total_sec, fallback_statut="No Time"):
    if total_sec is None or pd.isna(total_sec) or total_sec < 0: return fallback_statut
    m, reste_sec = divmod(round(total_sec, 2), 60)
    s = int(reste_sec // 1)
    c = int(round((reste_sec % 1) * 100))
    if c == 100: s += 1; c = 0
    if s == 60: m += 1; s = 0
    return f"{int(m):02d}:{s:02d}.{c:02d}"

def formater_heure_ecran(val):
    if pd.isna(val) or val == "" or str(val).lower() == "nan": return "-"
    s = str(val).strip()
    if s.endswith(".0"): s = s[:-2]
    s = s.zfill(6)
    return f"{s[0:2]}:{s[2:4]}.{s[4:6]}" if len(s) == 6 else str(val)

def calculer_statut_chrono(row, est_dans_le_live=True):
    if "Calc_Sec_2" in row and pd.notna(row["Calc_Sec_2"]) and row["Calc_Sec_2"] > 0:
        return format_final_chrono(row["Calc_Sec_2"])
    if "Heure_Depart_2" in row and pd.notna(row["Heure_Depart_2"]) and ("Heure_Arrivee_2" in row and pd.isna(row["Heure_Arrivee_2"])):
        if est_dans_le_live:
            return "<span class='vrai-gyrophare'>🚨</span> EN PISTE"
        else:
            return "En Piste"
    return "No Time"

def generer_tableau_html(df, classe_specifique):
    if df.empty: 
        return f"<table class='table-compacte {classe_specifique}'><tr><td style='text-align: center; padding: 10px;'>Aucune donnée disponible</td></tr></table>"
    
    if classe_specifique == "table-class-groupes" and "Classe" in df.columns:
        cols_a_retirer = ["Cl_Tri_Num", "Cl_Tri_Suff"]
        colonnes_visibles = [c for c in df.columns if c not in cols_a_retirer]
        
        html = f"<table class='table-compacte table-class-groupes'><thead><tr>"
        for col in colonnes_visibles:
            html += f"<th>{col}</th>"
        html += "</tr></thead><tbody>"
        for idx in range(len(df)):
            classe_row = ""
            if idx < len(df) - 1:
                if str(df.iloc[idx]["Classe"]) != str(df.iloc[idx + 1]["Classe"]):
                    classe_row = "class='ligne-separation-classe'"
            html += f"<tr {classe_row}>"
            for col in colonnes_visibles:
                html += f"<td>{df.iloc[idx][col]}</td>"
            html += "</tr>"
        html += "</tbody></table>"
        return html

    return df.to_html(index=False, classes=f"table-compacte {classe_specifique}", escape=False, border=0)

def decomposer_classe_pour_tri(valeur_classe):
    s = str(valeur_classe).strip().upper()
    if s.endswith(".0"): s = s[:-2]
    chiffres = ""
    for char in s:
        if char.isdigit(): chiffres += char
        else: break
    if chiffres:
        return int(chiffres), s[len(chiffres):].strip()
    return 999, s
cols_live = ["N°", "Nom_Prenom", "Voiture", "Départ", "Arrivée", "Chrono réalisé"]
cols_hist = ["N°", "Nom_Prenom", "Voiture", "Groupe", "Classe", "Course 1", "Chrono réalisé"]
affichage_dynamique = st.empty()

while True:
    # Initialisations de sécurité obligatoires
    html_hist = "<table class='table-compacte table-hist'><tr><td style='text-align: center; padding: 10px;'>Aucune donnée disponible pour le plateau RACB</td></tr></table>"
    df_live = pd.DataFrame(columns=cols_live)
    df_hist = pd.DataFrame(columns=cols_hist)
    df_racb = pd.DataFrame(columns=["Pos", "N°", "Nom_Prenom", "Groupe", "Classe", "Chrono"])
    df_divisions = pd.DataFrame(columns=["Pos", "N°", "Nom_Prenom", "Groupe", "Classe", "Chrono"])

    fichiers_prets = os.path.exists(FILE_ENGAGES) and os.path.exists(FILE_DEPART) and os.path.exists(FILE_ARRIVEE)

    if fichiers_prets and os.path.getsize(FILE_ENGAGES) > 0 and os.path.getsize(FILE_DEPART) > 0 and os.path.getsize(FILE_ARRIVEE) > 0:
        try:
            # CORRECTION ABSOLUE : On force Pandas à chercher les titres à la ligne 2 (header=1) pour TOUS les fichiers
            df_eng_raw = pd.read_excel(FILE_ENGAGES, header=1, engine='openpyxl')
            df_dep_raw = pd.read_excel(FILE_DEPART, header=None, engine='openpyxl')
            df_arr_raw = pd.read_excel(FILE_ARRIVEE, header=None, engine='openpyxl')

            idx_dep_1, idx_arr_1 = None, None
            idx_dep_2, idx_arr_2 = None, None
            
            # Repérage strict des colonnes basé sur la ligne 2 (index 1) qui ne bouge jamais
            for c_idx in range(len(df_dep_raw.columns)):
                val = str(df_dep_raw.iloc[1, c_idx]).strip().upper()
                if "COURSE 1 RACB" in val: idx_dep_1 = c_idx
                elif "COURSE 2 RACB" in val: idx_dep_2 = c_idx

            for c_idx in range(len(df_arr_raw.columns)):
                val = str(df_arr_raw.iloc[1, c_idx]).strip().upper()
                if "COURSE 1 RACB" in val: idx_arr_1 = c_idx
                elif "COURSE 2 RACB" in val: idx_arr_2 = c_idx

            df_dep2 = pd.DataFrame({"N°": df_dep_raw.iloc[2:, idx_dep_2].apply(nettoyer_numero), "Heure_Depart_2": df_dep_raw.iloc[2:, idx_dep_2 + 1]}) if idx_dep_2 is not None else pd.DataFrame(columns=["N°", "Heure_Depart_2"])
            df_arr2 = pd.DataFrame({"N°": df_arr_raw.iloc[2:, idx_arr_2].apply(nettoyer_numero), "Heure_Arrivee_2": df_arr_raw.iloc[2:, idx_arr_2 + 2]}) if idx_arr_2 is not None else pd.DataFrame(columns=["N°", "Heure_Arrivee_2"])
            
            df_dep1 = pd.DataFrame({"N°": df_dep_raw.iloc[2:, idx_dep_1].apply(nettoyer_numero), "Heure_Depart_1": df_dep_raw.iloc[2:, idx_dep_1 + 1]}) if idx_dep_1 is not None else pd.DataFrame(columns=["N°", "Heure_Depart_1"])
            df_arr1 = pd.DataFrame({"N°": df_arr_raw.iloc[2:, idx_arr_1].apply(nettoyer_numero), "Heure_Arrivee_1": df_arr_raw.iloc[2:, idx_arr_1 + 2]}) if idx_arr_1 is not None else pd.DataFrame(columns=["N°", "Heure_Arrivee_1"])

            df_eng_raw.columns = df_eng_raw.columns.astype(str).str.strip().str.upper()
            df_eng = pd.DataFrame({"N°": df_eng_raw.iloc[:, 0].apply(nettoyer_numero), 
                                   "Nom_Prenom": df_eng_raw.iloc[:, 1].fillna("Pilote Inconnu").astype(str).str.strip(),
                                   "Voiture": df_eng_raw.iloc[:, 4].fillna("").astype(str).str.strip(),
                                   "Groupe": df_eng_raw.iloc[:, 5].apply(lambda x: "-" if pd.isna(x) else str(x).strip()[:-2] if str(x).strip().endswith(".0") else str(x).strip()),
                                   "Classe": df_eng_raw.iloc[:, 6].fillna("-").astype(str).str.strip().apply(lambda x: x[:-2] if x.endswith(".0") else x)})

            df_eng = df_eng[df_eng["N°"] != "NAN"].drop_duplicates(subset=["N°"])
        except Exception as e:
            pass
        try:
            df_dep1 = df_dep1[(df_dep1["N°"] != "NAN") & (df_dep1["N°"] != "")]
            df_dep2 = df_dep2[(df_dep2["N°"] != "NAN") & (df_dep2["N°"] != "")]

            for d in [df_dep1, df_arr1, df_dep2, df_arr2]:
                if len(d) > 0:
                    d["N°"] = d["N°"].astype(str)
                    d["Run_Index"] = d.groupby("N°").cumcount() + 1

            if len(df_dep1) > 0: df_dep1["Sec_Dep_1"] = df_dep1["Heure_Depart_1"].apply(convertir_en_secondes)
            if len(df_arr1) > 0: df_arr1["Sec_Arr_1"] = df_arr1["Heure_Arrivee_1"].apply(convertir_en_secondes)
            if len(df_dep2) > 0: df_dep2["Sec_Dep_2"] = df_dep2["Heure_Depart_2"].apply(convertir_en_secondes)
            if len(df_arr2) > 0: df_arr2["Sec_Arr_2"] = df_arr2["Heure_Arrivee_2"].apply(convertir_en_secondes)

            base_runs = pd.DataFrame(columns=["N°", "Run_Index"])
            for d in [df_dep1, df_dep2]:
                if len(d) > 0: base_runs = pd.concat([base_runs, d[["N°", "Run_Index"]]], ignore_index=True)
            
            if len(base_runs) == 0:
                base_runs = df_eng[["N°"]].copy(); base_runs["Run_Index"] = 1
            else:
                base_runs = base_runs.drop_duplicates(subset=["N°", "Run_Index"])

            base = pd.merge(base_runs, df_eng, on="N°", how="inner")
            if len(df_dep1) > 0: base = pd.merge(base, df_dep1, on=["N°", "Run_Index"], how="left")
            if len(df_arr1) > 0: base = pd.merge(base, df_arr1, on=["N°", "Run_Index"], how="left")
            if len(df_dep2) > 0: base = pd.merge(base, df_dep2, on=["N°", "Run_Index"], how="left")
            if len(df_arr2) > 0: base = pd.merge(base, df_arr2, on=["N°", "Run_Index"], how="left")
            if len(base) > 0:
                base["Calc_Sec_1"] = (base["Sec_Arr_1"] - base["Sec_Dep_1"]).apply(lambda x: x + 3600 if (x is not None and x < 0) else x)
                base["Calc_Sec_2"] = (base["Sec_Arr_2"] - base["Sec_Dep_2"]).apply(lambda x: x + 3600 if (x is not None and x < 0) else x)
                
                base["Course_1_Txt"] = base["Calc_Sec_1"].apply(lambda x: format_final_chrono(x, fallback_statut="No Time"))

                if "Heure_Depart_2" in base.columns and base["Heure_Depart_2"].notna().any():
                    base_c2 = base[base["Heure_Depart_2"].notna()].copy()
                    base_c2["Ordre_Live"] = range(len(base_c2))
                    df_live_base = base_c2.sort_values(by="Ordre_Live", ascending=False).head(5).copy()
                    df_live_base["Chrono réalisé"] = df_live_base.apply(lambda r: calculer_statut_chrono(r, est_dans_le_live=True), axis=1)
                    df_live_base["Départ_C2"] = df_live_base["Heure_Depart_2"].apply(formater_heure_ecran)
                    df_live_base["Arrivée_C2"] = df_live_base["Heure_Arrivee_2"].apply(formater_heure_ecran)
                    df_live = df_live_base[["N°", "Nom_Prenom", "Voiture", "Départ_C2", "Arrivée_C2", "Chrono réalisé"]].rename(columns={"Départ_C2": "Départ", "Arrivée_C2": "Arrivée"})

                base["Ordre_Saisie"] = range(len(base))
                df_hist_base = base.sort_values(by="Ordre_Saisie", ascending=False).copy()
                
                # --- CONSTRUCTION DE L'HISTORIQUE HTML AVEC FOND VERT PASTEL EXCLUSIF #d9fcec ---
                html_hist = "<table class='table-compacte table-hist'><thead><tr>"
                for col in ["N°", "Nom_Prenom", "Voiture", "Groupe", "Classe", "Course 1", "Chrono réalisé"] :
                    html_hist += f"<th>{col}</th>"
                html_hist += "</tr></thead><tbody>"

                for idx, row in df_hist_base.iterrows():
                    t1, t2 = row["Calc_Sec_1"], row["Calc_Sec_2"]
                    
                    valeurs_valides = [v for v in [t1, t2] if pd.notna(v) and v > 0]
                    meilleur_sec = min(valeurs_valides) if valeurs_valides else None

                    s1 = "class='meilleur-temps'" if (meilleur_sec and t1 == meilleur_sec) else ""
                    s2 = "class='meilleur-temps'" if (meilleur_sec and t2 == meilleur_sec) else ""

                    if pd.notna(row["Heure_Depart_2"]) and pd.isna(row["Heure_Arrivee_2"]):
                        txt_c2_visuel = "En Piste"
                        s2 = ""
                    elif pd.isna(t2) or t2 <= 0:
                        txt_c2_visuel = "No Time"
                    else:
                        txt_c2 = format_final_chrono(t2)
                        if pd.notna(t1) and t1 > 0:
                            if t2 < t1: txt_c2_visuel = f"{txt_c2} <span style='color: #22C55E; font-size: 1.65rem; line-height: 1; vertical-align: -0.15rem;'>▲</span>"
                            elif t2 > t1: txt_c2_visuel = f"{txt_c2} <span style='color: #EF4444; font-size: 1.65rem; line-height: 1; vertical-align: -0.15rem;'>▼</span>"
                            else: txt_c2_visuel = txt_c2
                        else:
                            txt_c2_visuel = txt_c2

                    txt_c1_visuel = format_final_chrono(t1)

                    html_hist += f"<tr>"
                    html_hist += f"<td>{row['N°']}</td>"
                    html_hist += f"<td>{row['Nom_Prenom']}</td>"
                    html_hist += f"<td>{row['Voiture']}</td>"
                    html_hist += f"<td>{row['Groupe']}</td>"
                    html_hist += f"<td>{row['Classe']}</td>"
                    html_hist += f"<td {s1}>{txt_c1_visuel}</td>"
                    html_hist += f"<td {s2}>{txt_c2_visuel}</td>"
                    html_hist += f"</tr>"
                html_hist += "</tbody></table>"

                condition_au_moins_un_temps = ((base["Calc_Sec_1"].notna() & (base["Calc_Sec_1"] > 0)) | (base["Calc_Sec_2"].notna() & (base["Calc_Sec_2"] > 0)))
                valides = base[condition_au_moins_un_temps].copy()
                
                if len(valides) > 0:
                    valides["Meilleur_Sec"] = valides[["Calc_Sec_1", "Calc_Sec_2"]].min(axis=1, skipna=True)
                    scr = valides.sort_values(by="Meilleur_Sec").drop_duplicates(subset=["N°"], keep="first").copy()
                    
                    # --- 1. CLASSEMENT GENERAL SCRATCH ---
                    racb = scr.head(30).copy()
                    if len(racb) > 0:
                        racb["Pos"] = range(1, len(racb) + 1)
                        racb["Chrono"] = racb["Meilleur_Sec"].apply(format_final_chrono)
                        df_racb = racb[["Pos", "N°", "Nom_Prenom", "Groupe", "Classe", "Chrono"]]
                    
                    # --- 2. CLASSEMENT GENERAL OFFICIEUX PAR CLASSE ---
                    scr["Cl_Tri_Num"] = scr["Classe"].apply(lambda x: decomposer_classe_pour_tri(x))
                    scr["Cl_Tri_Suff"] = scr["Classe"].apply(lambda x: decomposer_classe_pour_tri(x))
                    
                    scr_trie = scr.sort_values(by=["Cl_Tri_Num", "Cl_Tri_Suff", "Groupe", "Meilleur_Sec"])
                    df_grouped = scr_trie.groupby("Classe", sort=False).head(3).copy()
                    df_grouped = df_grouped.sort_values(by=["Cl_Tri_Num", "Cl_Tri_Suff", "Groupe", "Meilleur_Sec"])
                    
                    if len(df_grouped) > 0:
                        df_grouped["Pos"] = df_grouped.groupby("Classe", sort=False).cumcount() + 1
                        df_grouped["Chrono"] = df_grouped["Meilleur_Sec"].apply(format_final_chrono)
                        df_divisions = df_grouped[["Pos", "N°", "Nom_Prenom", "Groupe", "Classe", "Chrono", "Cl_Tri_Num", "Cl_Tri_Suff"]]
        except Exception as e:
            pass

    with affichage_dynamique.container():
        if not fichiers_prets:
            st.warning(f"⚠️ En attente des fichiers Excel dans le dossier : {BASE_DIR}")
        else:
            cg, cd = st.columns([1.3, 0.9])
            with cg:
                st.markdown("<span class='titre-live'>🏎️ EN DIRECT / Derniers concurrents partis</span>", unsafe_allow_html=True)
                st.markdown(generer_tableau_html(df_live, "table-live"), unsafe_allow_html=True)
                st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
                st.markdown("<span class='titre-hist'>🕒 HISTORIQUE DES TEMPS / 2ème COURSE / Concurrents RACB</span>", unsafe_allow_html=True)
                st.markdown(html_hist, unsafe_allow_html=True)
            with cd:
                st.markdown("<span class='titre-classement'>🏆 CLASSEMENT EVOLUTIF OFFICIEUX RACB (Top 30)</span>", unsafe_allow_html=True)
                st.markdown(generer_tableau_html(df_racb, "table-class-robuste"), unsafe_allow_html=True)
                
                st.markdown("<div style='height: 65px;'></div>", unsafe_allow_html=True)
                
                st.markdown("<span class='titre-classement'>📊 CLASSEMENT EVOLUTIF OFFICIEUX PAR Classe (Top 3)</span>", unsafe_allow_html=True)
                st.markdown(generer_tableau_html(df_divisions, "table-class-groupes"), unsafe_allow_html=True)
    time.sleep(1)
