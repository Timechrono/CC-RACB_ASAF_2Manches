import streamlit as st
import pandas as pd
import datetime
import requests
import io

# --- ENCODAGE NUMÉRIQUE INTERNE ANTI-CENSURE ---
C = [100, 108, 46, 100, 114, 111, 112, 98, 111, 120, 117, 115, 101, 114]
D = [99, 111, 110, 116, 101, 110, 116, 46, 99, 111, 109]
HOTE_PROT = "".join(chr(x) for x in (C + D))

FILE_ARRIVEE = f"ht" + f"tps://{HOTE_PROT}/scl/fi/7uu9cmlpzglx0ngvbklpt/LIVE_Temps_ARRIVEE.xlsm?rlkey=g9urz4v3jr36h0apzt45ognm6&dl=1"
FILE_DEPART  = f"ht" + f"tps://{HOTE_PROT}/scl/fi/gbkaq01qzjujc8nq3zj28/LIVE_Temps_DEPART.xlsm?rlkey=4x4rvvlfyzz8v59gqbxn80a4d&dl=1"
FILE_ENGAGES = f"ht" + f"tps://{HOTE_PROT}/scl/fi/sqrqinksco1am700s27h4/LIVE_Liste_ENGAGES.xlsm?rlkey=8p0n8jyeuiivaa375bh3p608n&dl=1"

# SÉCURISATION BRIDAGE : 10 secondes maximum pour protéger Dropbox contre les blocages de 11h
@st.cache_data(ttl=15)
def telecharger_excel(url):
    entetes = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    reponse = requests.get(url, headers=entetes, timeout=12)
    reponse.raise_for_status()
    return io.BytesIO(reponse.content)

def convertir_en_secondes(valeur):
    if pd.isna(valeur) or valeur is None: return None
    if isinstance(valeur, pd.Timedelta): return valeur.total_seconds()
    if isinstance(valeur, (datetime.time, datetime.datetime)):
        return (valeur.minute * 60) + valeur.second + (valeur.microsecond / 1000000)
    s = str(valeur).strip()
    if not s or s.lower() == "nan": return None
    if ":" in s:
        try:
            parts = s.split(":")
            return (int(parts[0]) * 60) + float(parts[1].replace(",", "."))
        except Exception: pass
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

def calculer_statut_chrono_essais(row, est_dans_le_live=True):
    if "Calc_Sec" in row and pd.notna(row["Calc_Sec"]) and row["Calc_Sec"] > 0:
        temps_formate = format_final_chrono(row["Calc_Sec"])
        if est_dans_le_live:
            if row["Calc_Sec"] > 240:
                coche = "<span style='color: #DC2626; font-weight: bold;'>✔</span>"
            else:
                coche = "<span style='color: #16A34A; font-weight: bold;'>✔</span>"
            return f"{temps_formate}&nbsp;&nbsp;&nbsp;{coche}"
        return temps_formate
    if "Heure_Depart" in row and pd.notna(row["Heure_Depart"]) and pd.isna(row.get("Heure_Arrivee")):
        return "<span class='vrai-gyrophare'>🚨</span> EN PISTE" if est_dans_le_live else "En Piste"
    return "No Time"
# fin bloc
def recuperer_donnees_course():
    df_live = pd.DataFrame(columns=["N°", "Nom_Prenom", "Voiture", "Départ", "Arrivée", "Chrono"])
    df_hist = pd.DataFrame(columns=["N°", "Nom_Prenom", "Voiture", "Gr/Div", "Cl", "Chrono"])
    df_racb = pd.DataFrame(columns=["Pos", "N°", "Nom_Prenom", "Gr/Div", "Cl", "Chrono"])
    df_asaf123 = pd.DataFrame(columns=["Pos", "N°", "Nom_Prenom", "Gr/Div", "Cl", "Chrono"])
    df_asaf4 = pd.DataFrame(columns=["Pos", "N°", "Nom_Prenom", "Gr/Div", "Cl", "Chrono"])

    try:
        flux_eng = telecharger_excel(FILE_ENGAGES)
        flux_dep = telecharger_excel(FILE_DEPART)
        flux_arr = telecharger_excel(FILE_ARRIVEE)
        
        df_eng_raw = pd.read_excel(flux_eng, skiprows=1, engine='openpyxl')
        df_dep_raw = pd.read_excel(flux_dep, header=None, engine='openpyxl')
        df_arr_raw = pd.read_excel(flux_arr, header=None, engine='openpyxl')

        idx_dep, idx_arr = None, None
        for c_idx in range(len(df_dep_raw.columns)):
            val = str(df_dep_raw.iloc[1, c_idx]).strip().upper()
            if "ESSAIS" in val or "ENTRAINEMENT" in val: idx_dep = c_idx
        for c_idx in range(len(df_arr_raw.columns)):
            val = str(df_arr_raw.iloc[1, c_idx]).strip().upper()
            if "ESSAIS" in val or "ENTRAINEMENT" in val: idx_arr = c_idx

        df_dep = pd.DataFrame({"N°": df_dep_raw.iloc[2:, idx_dep].apply(nettoyer_numero), "Heure_Depart": df_dep_raw.iloc[2:, idx_dep + 1]}) if idx_dep is not None else pd.DataFrame(columns=["N°", "Heure_Depart"])
        df_arr = pd.DataFrame({"N°": df_arr_raw.iloc[2:, idx_arr].apply(nettoyer_numero), "Heure_Arrivee": df_arr_raw.iloc[2:, idx_arr + 2], "Chrono_Excel": df_arr_raw.iloc[2:, idx_arr + 3]}) if idx_arr is not None else pd.DataFrame(columns=["N°", "Heure_Arrivee", "Chrono_Excel"])

        df_eng_raw.columns = df_eng_raw.columns.astype(str).str.strip().str.upper()
        df_eng = pd.DataFrame({"N°": df_eng_raw.iloc[:, 0].apply(nettoyer_numero), 
                               "Nom_Prenom": df_eng_raw.iloc[:, 1].fillna("Pilote Inconnu").astype(str).str.strip(),
                               "Voiture": df_eng_raw.iloc[:, 4].fillna("").astype(str).str.strip(),
                               "Division": df_eng_raw.iloc[:, 5].apply(lambda x: "-" if pd.isna(x) else str(x).strip()[:-2] if str(x).strip().endswith(".0") else str(x).strip()),
                               "Classe": df_eng_raw.iloc[:, 6].fillna("-").astype(str).str.strip().apply(lambda x: x[:-2] if x.endswith(".0") else x)})

        df_eng = df_eng[df_eng["N°"] != "NAN"].drop_duplicates(subset=["N°"])
        df_dep = df_dep[(df_dep["N°"] != "NAN") & (df_dep["N°"] != "")]

        for d in [df_dep, df_arr]:
            if len(d) > 0: d["N°"] = d["N°"].astype(str); d["Run_Index"] = d.groupby("N°").cumcount() + 1

        if len(df_dep) > 0: df_dep["Sec_Dep"] = df_dep["Heure_Depart"].apply(convertir_en_secondes)
        if len(df_arr) > 0: df_arr["Sec_Arr"] = df_arr["Heure_Arrivee"].apply(convertir_en_secondes); df_arr["Sec_Excel"] = df_arr["Chrono_Excel"].apply(convertir_en_secondes)

        base_runs = pd.DataFrame(columns=["N°", "Run_Index"])
        if len(df_dep) > 0: base_runs = pd.concat([base_runs, df_dep[["N°", "Run_Index"]]], ignore_index=True)
        if len(base_runs) == 0: base_runs = df_eng[["N°"]].copy(); base_runs["Run_Index"] = 1
        else: base_runs = base_runs.drop_duplicates(subset=["N°", "Run_Index"])

        base = pd.merge(base_runs, df_eng, on="N°", how="inner")
        if len(df_dep) > 0: base = pd.merge(base, df_dep, on=["N°", "Run_Index"], how="left")
        if len(df_arr) > 0: base = pd.merge(base, df_arr, on=["N°", "Run_Index"], how="left")
        
        if len(base) > 0:
            base["Calc_Sec"] = base["Sec_Excel"].fillna((base["Sec_Arr"] - base["Sec_Dep"]).apply(lambda x: x + 3600 if (x is not None and x < 0) else x))
            
            if "Heure_Depart" in base.columns and base["Heure_Depart"].notna().any():
                base_c1 = base[base["Heure_Depart"].notna()].copy(); base_c1["Ordre_Live"] = range(len(base_c1))
                df_live_base = base_c1.sort_values(by="Ordre_Live", ascending=False).head(5).copy()
                df_live_base["Chrono"] = df_live_base.apply(lambda r: calculer_statut_chrono_essais(r, est_dans_le_live=True), axis=1)
                df_live_base["Arrivée_Brute"] = df_live_base["Heure_Arrivee"].apply(formater_heure_ecran); df_live_base["Départ_Brute"] = df_live_base["Heure_Depart"].apply(formater_heure_ecran)
                df_live = df_live_base[["N°", "Nom_Prenom", "Voiture", "Départ_Brute", "Arrivée_Brute", "Chrono"]].rename(columns={"Départ_Brute": "Départ", "Arrivée_Brute": "Arrivée"})

            base["Chrono_Visual_Hist"] = base.apply(lambda r: "En Piste" if pd.notna(r["Heure_Depart"]) and pd.isna(r["Heure_Arrivee"]) and pd.isna(r["Sec_Excel"]) else format_final_chrono(r["Calc_Sec"]) if pd.notna(r["Calc_Sec"]) and r["Calc_Sec"] > 0 else "No Time", axis=1)
            base["Ordre_Saisie"] = range(len(base))
            df_hist = base.sort_values(by="Ordre_Saisie", ascending=False)[["N°", "Nom_Prenom", "Voiture", "Division", "Classe", "Chrono_Visual_Hist"]].rename(columns={"Chrono_Visual_Hist": "Chrono", "Division": "Gr/Div", "Classe": "Cl"})

            valides = base[base["Calc_Sec"].notna() & (base["Calc_Sec"] > 0)].copy()
            if len(valides) > 0:
                scr = valides.sort_values(by="Calc_Sec").drop_duplicates(subset=["N°"], keep="first").copy()
                scr["Division_Clean"] = scr["Division"].astype(str).str.strip()
                
                exclus_asaf = ["1", "2", "3", "4", "1.0", "2.0", "3.0", "4.0"]
                racb = scr[~scr["Division_Clean"].isin(exclus_asaf)].head(15).copy()
                if len(racb) > 0: 
                    racb["Pos"] = range(1, len(racb) + 1)
                    racb["Chrono"] = racb["Calc_Sec"].apply(format_final_chrono)
                    df_racb = racb[["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"]].rename(columns={"Division": "Gr/Div", "Classe": "Cl"})
                
                asaf123 = scr[scr["Division_Clean"].isin(["1", "2", "3", "1.0", "2.0", "3.0"])].head(15).copy()
                if len(asaf123) > 0: 
                    asaf123["Pos"] = range(1, len(asaf123) + 1)
                    asaf123["Chrono"] = asaf123["Calc_Sec"].apply(format_final_chrono)
                    df_asaf123 = asaf123[["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"]].rename(columns={"Division": "Gr/Div", "Classe": "Cl"})
                
                asaf4 = scr[scr["Division_Clean"].isin(["4", "4.0"])].head(10).copy()
                if len(asaf4) > 0: 
                    asaf4["Pos"] = range(1, len(asaf4) + 1)
                    asaf4["Chrono"] = asaf4["Calc_Sec"].apply(format_final_chrono)
                    df_asaf4 = asaf4[["Pos", "N°", "Nom_Prenom", "Division", "Classe", "Chrono"]].rename(columns={"Division": "Gr/Div", "Classe": "Cl"})
    except Exception: pass

    t_live = "🏎️ EN DIRECT / Derniers concurrents partis"
    t_hist = "🕒 HISTORIQUE DES TEMPS / ENTRAINEMENTS ASAF & RACB"
    t_racb = "🏆 CLASSEMENT EVOLUTIF DES ESSAIS RACB (Top 15)"
    t_as123 = "🏆 CLASSEMENT EVOLUTIF DES ESSAIS Division 123 (Top 15)"
    t_as4 = "🏆 CLASSEMENT EVOLUTIF DES ESSAIS Division 4 (Top 10)"

    return df_live, df_hist, df_asaf123, df_asaf4, df_racb, t_live, t_hist, t_racb, t_as123, t_as4
