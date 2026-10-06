import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import time
import io
import requests

st.cache_data.clear()

# --- DESIGN SCIENTIFIQUE RIGIDE RESTAURÉ ---
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    .vrai-gyrophare { display: inline-block; margin-right: 6px; font-size: 1.05rem !important; vertical-align: middle !important; }
    .titre-live, .titre-hist, .titre-classement {
        color: #FFFFFF !important; font-size: 1.05rem !important; font-weight: bold !important;
        padding: 4px 8px !important; border-radius: 3px !important; margin-bottom: 6px !important;
        width: 100% !important; display: block !important; clear: both !important;
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
    .table-compacte td.meilleur-temps { background-color: #d9fcec !important; color: #000000 !important; font-weight: bold !important; }
    .table-class-robuste tr:nth-child(odd) td { background-color: #E0F2FE !important; }
    .table-class-groupes tr.ligne-separation-classe td { border-bottom: 2px solid #1E3A8A !important; }
    
    .table-live th:nth-child(1), .table-live td:nth-child(1) { width: 8% !important; }
    .table-live th:nth-child(2), .table-live td:nth-child(2) { width: 26% !important; }
    .table-live th:nth-child(3), .table-live td:nth-child(3) { width: 18% !important; }
    .table-live th:nth-child(4), .table-live td:nth-child(4) { width: 13% !important; }
    .table-live th:nth-child(5), .table-live td:nth-child(5) { width: 13% !important; }
    .table-live th:nth-child(6), .table-live td:nth-child(6) { width: 22% !important; }

    .table-hist th:nth-child(1), .table-hist td:nth-child(1) { width: 6% !important; }   
    .table-hist th:nth-child(2), .table-hist td:nth-child(2) { width: 23% !important; }  
    .table-hist th:nth-child(3), .table-hist td:nth-child(3) { width: 21% !important; }  
    .table-hist th:nth-child(4), .table-hist td:nth-child(4) { width: 10% !important; }   
    .table-hist th:nth-child(5), .table-hist td:nth-child(5) { width: 6% !important; }   
    .table-hist th:nth-child(6), .table-hist td:nth-child(15) { width: 15% !important; }  
    .table-hist th:nth-child(7), .table-hist td:nth-child(19) { width: 19% !important; }  
    .zone-defilement-tactile { width: 100% !important; overflow-x: auto !important; display: block !important; }
    </style>
""", unsafe_allow_html=True)
BASE_DIR = "Dropbox Cloud"
C = [100, 108, 46, 100, 114, 111, 112, 98, 111, 120, 117, 115, 101, 114]
D = [99, 111, 110, 116, 101, 110, 116, 46, 99, 111, 109]
HOTE_PROT = "".join(chr(x) for x in (C + D))

FILE_ARRIVEE = f"https://{HOTE_PROT}/scl/fi/7uu9cmlpzglx0ngvbklpt/LIVE_Temps_ARRIVEE.xlsm?rlkey=g9urz4v3jr36h0apzt45ognm6&dl=1"
FILE_DEPART  = f"https://{HOTE_PROT}/scl/fi/gbkaq01qzjujc8nq3zj28/LIVE_Temps_DEPART.xlsm?rlkey=4x4rvvlfyzz8v59gqbxn80a4d&dl=1"
FILE_ENGAGES = f"https://{HOTE_PROT}/scl/fi/sqrqinksco1am700s27h4/LIVE_Liste_ENGAGES.xlsm?rlkey=8p0n8jyeuiivaa375bh3p608n&dl=1"

@st.cache_data(ttl=15)
def telecharger_excel(url):
    try:
        entetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        reponse = requests.get(url, headers=entetes, timeout=12)
        return io.BytesIO(reponse.content)
    except Exception: return None

def convertir_en_secondes(valeur):
    if pd.isna(valeur) or valeur is None: return None
    if isinstance(valeur, (datetime.time, datetime.datetime)):
        return (valeur.minute * 60) + valeur.second + (valeur.microsecond / 1000000)
    s = str(valeur).strip()
    if s.endswith(".0"): s = s[:-2]
    s_clean = "".join([c for c in s if c.isdigit()])
    if not s_clean or len(s_clean) < 3: return None
    num = int(s_clean)
    if num > 595999: return None
    centiemes = num % 100
    secondes = (num // 100) % 100
    minutes = num // 10000
    return (minutes * 60) + secondes + (centiemes / 100)

def nettoyer_numero(valeur):
    if pd.isna(valeur): return "nan"
    s = str(valeur).strip().upper()
    return s[:-2] if s.endswith(".0") else s

def format_final_chrono(total_sec, fallback_statut="No Time"):
    if total_sec is None or pd.isna(total_sec) or total_sec < 0 or total_sec == float('inf'): return fallback_statut
    m, reste_sec = divmod(round(total_sec, 2), 60)
    return f"{int(m):02d}:{int(reste_sec // 1):02d}.{int(round((reste_sec % 1) * 100)):02d}".replace(".100", ".00")

def formater_heure_ecran(val):
    if pd.isna(val) or val == "" or str(val).lower() == "nan": return "-"
    s = str(val).strip()
    if s.endswith(".0"): s = s[:-2]
    s = s.zfill(6)
    return f"{s[0:2]}:{s[2:4]}.{s[4:6]}" if len(s) == 6 else str(val)

def calculer_statut_chrono_live(valeur_sec):
    if pd.isna(valeur_sec) or valeur_sec <= 0: return "No Time"
    return f"{format_final_chrono(valeur_sec)} &nbsp;<span style='color: #22C55E;'>✓</span>"

def generer_tableau_html(df, cls_spec):
    if df.empty: return "<div class='zone-defilement-tactile'><table class='table-compacte'><tr><td>Aucune donnée</td></tr></table></div>"
    return f"<div class='zone-defilement-tactile'>{df.to_html(index=False, classes=f'table-compacte {cls_spec}', escape=False, border=0)}</div>"
def recuperer_donnees_course():
    df_live = pd.DataFrame(columns=["N°", "Nom_Prenom", "Voiture", "Départ", "Arrivée", "Chrono réalisé"])
    df_asaf123 = pd.DataFrame(columns=["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"])
    df_asaf4 = pd.DataFrame(columns=["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"])
    html_hist = "<div class='zone-defilement-tactile'><table class='table-compacte'><tr><td>Aucune donnée</td></tr></table></div>"
    df_divisions = html_hist

    t_live = "🏎️ EN DIRECT / Derniers Concurrents partis"
    t_his = "🕒 HISTORIQUE DES TEMPS / ASAF"
    t_haut = "🏆 CLASSEMENT GENERAL OFFICIEUX Division 123 (Top 25)"
    t_milieu = "🏆 CLASSEMENT GENERAL OFFICIEUX Division 4 (Top 10)"
    t_bas = "📊 CLASSEMENT OFFICIEUX par Division / Classe (Top 3)"

    try:
        flux_eng = telecharger_excel(FILE_ENGAGES)
        flux_arr = telecharger_excel(FILE_ARRIVEE)
        
        if flux_eng is not None and flux_arr is not None:
            df_eng_raw = pd.read_excel(flux_eng, skiprows=1, engine='openpyxl')
            df_arr_raw = pd.read_excel(flux_arr, header=None, engine='openpyxl')

            df_eng = pd.DataFrame({
                "N°": df_eng_raw.iloc[:, 0].apply(nettoyer_numero), 
                "Nom_Prenom": df_eng_raw.iloc[:, 1].fillna("Pilote Inconnu").astype(str).str.strip(),
                "Voiture": df_eng_raw.iloc[:, 4].fillna("").astype(str).str.strip(),
                "Division": df_eng_raw.iloc[:, 5].astype(str).str.strip().apply(lambda x: x[:-2] if x.endswith(".0") else x),
                "Classe": df_eng_raw.iloc[:, 6].fillna("-").astype(str).str.strip().apply(lambda x: x[:-2] if x.endswith(".0") else x)
            })
            
            # 1. EXCLUSION DE LA LETTRE "N"
            df_eng = df_eng[~df_eng["N°"].str.startswith("N", na=False)].copy()
            
            # 2. EXCLUSION STRICTE DES NUMÉROS ENTRE 900 ET 999
            df_eng["Num_Tri_Sec"] = pd.to_numeric(df_eng["N°"], errors='coerce').fillna(-1)
            df_eng = df_eng[~((df_eng["Num_Tri_Sec"] >= 900) & (df_eng["Num_Tri_Sec"] <= 999))].copy()
            df_eng = df_eng.drop(columns=["Num_Tri_Sec"])
            
            df_eng = df_eng[df_eng["N°"] != "NAN"].drop_duplicates(subset=["N°"])
            tous_numeros_autorises_asaf = set(df_eng["N°"].unique())

            def trouver_index_colonne_titre(df, chaine_recherche):
                for c_idx in range(len(df.columns)):
                    if chaine_recherche.upper() in str(df.iloc[1, c_idx]).strip().upper(): return c_idx
                return None

            def extraire_manche_selon_regles_asaf(df_arr_raw, nom_manche, label_cat):
                d_manche = {}
                col_dossard = trouver_index_colonne_titre(df_arr_raw, f"{nom_manche} {label_cat}")
                if col_dossard is None: return d_manche
                for r_idx in range(2, len(df_arr_raw)):
                    nv = nettoyer_numero(df_arr_raw.iloc[r_idx, col_dossard])
                    if nv in tous_numeros_autorises_asaf:
                        d_manche[nv] = {
                            "h_dep": df_arr_raw.iloc[r_idx, col_dossard + 1] if pd.notna(df_arr_raw.iloc[r_idx, col_dossard + 1]) else None, 
                            "h_arr": df_arr_raw.iloc[r_idx, col_dossard + 2] if pd.notna(df_arr_raw.iloc[r_idx, col_dossard + 2]) else None, 
                            "sec": convertir_en_secondes(df_arr_raw.iloc[r_idx, col_dossard + 3])
                        }
                return d_manche

            dict_c1 = extraire_manche_selon_regles_asaf(df_arr_raw, "COURSE 1", "ASAF")
            dict_c1.update({k: v for k, v in extraire_manche_selon_regles_asaf(df_arr_raw, "COURSE 1", "RACB").items() if k not in dict_c1 or dict_c1[k]["sec"] is None})
            dict_c2 = extraire_manche_selon_regles_asaf(df_arr_raw, "COURSE 2", "ASAF")
            dict_c2.update({k: v for k, v in extraire_manche_selon_regles_asaf(df_arr_raw, "COURSE 2", "RACB").items() if k not in dict_c2 or dict_c2[k]["sec"] is None})
            if not df_eng.empty:
                rows_data = []
                for _, pilot in df_eng.iterrows():
                    num = pilot["N°"]
                    rows_data.append({
                        "N°": num, "Nom_Prenom": pilot["Nom_Prenom"], "Voiture": pilot["Voiture"], "Division": pilot["Division"], "Classe": pilot["Classe"],
                        "Heure_Depart_3": dict_c2.get(num, {}).get("h_dep"), "Heure_Arrivee_3": dict_c2.get(num, {}).get("h_arr"),
                        "Calc_Sec_1": dict_c1.get(num, {}).get("sec"), "Calc_Sec_2": dict_c2.get(num, {}).get("sec")
                    })
                base = pd.DataFrame(rows_data)
                
                if len(base) > 0:
                    if "Heure_Depart_3" in base.columns and base["Heure_Depart_3"].notna().any():
                        base_c3 = base[base["Heure_Depart_3"].notna()].copy()
                        base_c3["Chrono réalisé"] = base_c3.apply(lambda r: calculer_statut_chrono_live(r["Calc_Sec_2"]) if pd.notna(r["Calc_Sec_2"]) else ("🚨 EN PISTE" if pd.isna(r["Heure_Arrivee_3"]) else "No Time"), axis=1)
                        base_c3["Départ"] = base_c3["Heure_Depart_3"].apply(formater_heure_ecran)
                        base_c3["Arrivée"] = base_c3["Heure_Arrivee_3"].apply(formater_heure_ecran)
                        df_live = base_c3.sort_values(by="Heure_Depart_3", ascending=False).head(5)[["N°", "Nom_Prenom", "Voiture", "Départ", "Arrivée", "Chrono réalisé"]]

                    df_hb = base[base["Calc_Sec_1"].notna() | base["Calc_Sec_2"].notna()].copy().sort_values(by="Heure_Depart_3", ascending=False, na_position="last")
                    
                    html_hist = "<div class='zone-defilement-tactile'><table class='table-compacte table-hist'><thead><tr><th>N°</th><th>Nom_Prenom</th><th>Voiture</th><th>Div</th><th>Cl</th><th>Course 1</th><th>Chrono</th></tr></thead><tbody>"
                    for idx, row in df_hb.iterrows():
                        t1, t2 = row["Calc_Sec_1"], row["Calc_Sec_2"]
                        txt_c1 = format_final_chrono(t1)
                        txt_c2 = f"<span style='color: #22C55E;'>•</span>&nbsp;{format_final_chrono(t2)}" if t2 else "No Time"
                        html_hist += f"<tr><td>{row['N°']}</td><td>{row['Nom_Prenom']}</td><td>{row['Voiture']}</td><td>{row['Division']}</td><td>{row['Classe']}</td><td>{txt_c1}</td><td>{txt_c2}</td></tr>"
                    html_hist += "</tbody></table></div>"
                    # CHANGEMENT DE MÉCANIQUE : On sélectionne le MINIMUM (meilleur temps unique) au lieu de la somme
                    def tri_val(r1, r2):
                        if pd.isna(r1) or pd.isna(r2) or r1 <= 0 or r2 <= 0: return float('inf')
                        return float(min(round(r1, 2), round(r2, 2)))
                    
                    base["Cumul_Sec"] = base.apply(lambda r: tri_val(r["Calc_Sec_1"], r["Calc_Sec_2"]), axis=1)
                    
                    base_valides = base[base["Cumul_Sec"] < float('inf')].sort_values(by="Cumul_Sec").copy()
                    base_invalides = base[base["Cumul_Sec"] == float('inf')].copy()
                    scr = pd.concat([base_valides, base_invalides]).drop_duplicates(subset=["N°"]).copy()
                    
                    # Verrous de sécurité anti-N et anti-900
                    scr = scr[~scr["N°"].str.startswith("N", na=False)].copy()
                    scr["Num_Filter_Check"] = pd.to_numeric(scr["N°"], errors='coerce').fillna(-1)
                    scr = scr[~((scr["Num_Filter_Check"] >= 900) & (scr["Num_Filter_Check"] <= 999))].copy()
                    scr = scr.drop(columns=["Num_Filter_Check"])
                    
                    if len(scr) > 0:
                        df_asaf123 = scr[scr["Division"].isin(["1", "2", "3"])].head(25).copy()
                        if not df_asaf123.empty:
                            df_asaf123["Pos"] = [str(i+1) if v < float('inf') else "-" for i, v in enumerate(df_asaf123["Cumul_Sec"])]
                            df_asaf123["Chrono"] = df_asaf123["Cumul_Sec"].apply(lambda val: format_final_chrono(val, "No Time"))
                            df_asaf123 = df_asaf123[["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"]]
                        
                        df_asaf4 = scr[scr["Division"] == "4"].head(10).copy()
                        if not df_asaf4.empty:
                            df_asaf4["Pos"] = [str(i+1) if v < float('inf') else "-" for i, v in enumerate(df_asaf4["Cumul_Sec"])]
                            df_asaf4["Chrono"] = df_asaf4["Cumul_Sec"].apply(lambda val: format_final_chrono(val, "No Time"))
                            df_asaf4 = df_asaf4[["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"]]
                        
                        scr["Classe_Tri"] = pd.to_numeric(scr["Classe"], errors='coerce').fillna(999)
                        df_grouped = scr.sort_values(by=["Division", "Classe_Tri", "Cumul_Sec"]).groupby(["Division", "Classe_Tri"]).head(3).copy()
                        if len(df_grouped) > 0:
                            hb = []
                            go = df_grouped.sort_values(by=["Division", "Classe_Tri", "Cumul_Sec"]).groupby(["Division", "Classe_Tri"])
                            tg, cg = len(go), 0
                            for (div, cl), g in go:
                                cg += 1; g = g.copy()
                                g["Pos"] = [str(i+1) if v < float('inf') else "-" for i, v in enumerate(g["Cumul_Sec"])]
                                g["Chrono"] = g["Cumul_Sec"].apply(lambda val: format_final_chrono(val, "No Time"))
                                sh = g[["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"]].rename(columns={"Division": "Div", "Classe": "Cl"}).to_html(index=False, header=(cg==1), classes='table-compacte table-class-groupes', escape=False, border=0)
                                if cg == 1: hb.append(sh.replace("</tbody>\n</table>", ""))
                                else: hb.append(sh.split("<tbody>")[-1].replace("</tbody>\n</table>", ""))
                                if cg < tg: hb.append("<tr class='ligne-separation-classe'><td colspan='6' style='padding:0 !important;'></td></tr>")
                            hb.append("</tbody>\n</table>")
                            df_divisions = "".join(hb)
    except Exception: pass
    return df_live, html_hist, df_asaf123, df_asaf4, df_divisions, t_live, t_his, t_haut, t_milieu, t_bas
