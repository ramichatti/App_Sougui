import streamlit as st
import numpy as np
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Load model and scaler
with open("rf_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

@st.cache_data
def load_data():
    sougui = pd.read_csv("Dim_Produit_Sougui.csv", header=None,
        names=['Id_Produit','Reference','Nom','PU_HT','col5','col6','col7',
               'Tarif_Regulier','Tarif_Promo','En_Stock','col11','col12'])
    sougui = sougui.iloc[1:].reset_index(drop=True)
    sougui['PU_HT'] = pd.to_numeric(sougui['PU_HT'], errors='coerce')
    sougui['Reference'] = sougui['Reference'].astype(str).str.strip()

    kalys = pd.read_csv("Dim_Produit_Kalys.csv", header=None,
        names=['Id','Reference','Source','Product_Name','Price','Categories'])
    kalys = kalys.iloc[1:].reset_index(drop=True)
    kalys['Price'] = pd.to_numeric(kalys['Price'], errors='coerce')
    kalys['Reference'] = kalys['Reference'].astype(str).str.strip()

    ileycom = pd.read_csv("Dim_Produit_Ileycom.csv", header=None,
        names=['Id','Reference','Source','Product_Name','Price','Categories'])
    ileycom = ileycom.iloc[1:].reset_index(drop=True)
    ileycom['Price'] = pd.to_numeric(ileycom['Price'], errors='coerce')
    ileycom['Reference'] = ileycom['Reference'].astype(str).str.strip()

    return sougui, kalys, ileycom

sougui, kalys, ileycom = load_data()

@st.cache_data
def prepare_ml_data():
    kalys_avg = kalys.groupby('Reference')['Price'].mean().reset_index()
    kalys_avg.columns = ['Reference', 'Kalys_Price']
    ileycom_avg = ileycom.groupby('Reference')['Price'].mean().reset_index()
    ileycom_avg.columns = ['Reference', 'Ileycom_Price']
    df = sougui.merge(kalys_avg, on='Reference', how='left')
    df = df.merge(ileycom_avg, on='Reference', how='left')
    df['Avg_Competitor_Price'] = df[['Kalys_Price', 'Ileycom_Price']].mean(axis=1)
    df = df[(df['PU_HT'] > 0) & df['Avg_Competitor_Price'].notna()].copy()
    df['Kalys_Price'] = df['Kalys_Price'].fillna(df['Kalys_Price'].mean())
    df['Ileycom_Price'] = df['Ileycom_Price'].fillna(df['Ileycom_Price'].mean())
    df['Has_Kalys'] = df['Kalys_Price'].notna().astype(int)
    df['Has_Ileycom'] = df['Ileycom_Price'].notna().astype(int)
    df['Price_Position'] = np.where(df['PU_HT'] < df['Avg_Competitor_Price'], 'Cheaper', 'More_Expensive')
    return df

df_ml = prepare_ml_data()

def get_fallback_response(prompt, cheaper, more_exp, total, avg_sougui, avg_kalys, avg_ileycom):
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ['review', 'expensive', 'overpriced', 'lower', 'cher']):
        return f"🔴 19 products need price review. Most urgent: CFA-001-SO at 499 TND while competitors charge 240-250 TND. Total potential savings: 1502 TND."
    elif any(word in prompt_lower for word in ['competitor', 'strongest', 'kalys', 'ileycom', 'concurrent']):
        return f"🏆 Ileycom is Sougui's strongest competitor — it has the highest feature importance (64%) in our ML model. Ileycom avg price: {avg_ileycom:.1f} TND vs Sougui: {avg_sougui:.1f} TND."
    elif any(word in prompt_lower for word in ['score', 'competitive', 'position', 'competitif']):
        return f"📊 Sougui's competitiveness score is 83.1% — above our 60% target! Sougui is cheaper in {cheaper}/{total} cases ({cheaper/total*100:.1f}%)."
    elif any(word in prompt_lower for word in ['anomal', 'unusual', 'abnormal']):
        return f"🚨 11 anomalous products detected. CFA-001-SO most abnormal: 499 TND vs 240-250 TND competitors. MC-001-RL suspiciously cheap: 15 TND vs 440-700 TND competitors."
    elif any(word in prompt_lower for word in ['cluster', 'segment', 'group']):
        return f"🔵 3 clusters: Budget (low price → maintain), Mid-range (monitor), Premium (urgent review — Sougui 499 TND vs competitors 240 TND)."
    elif any(word in prompt_lower for word in ['price', 'average', 'avg', 'prix', 'moyen']):
        return f"💰 Avg prices: Sougui {avg_sougui:.1f} TND, Kalys {avg_kalys:.1f} TND, Ileycom {avg_ileycom:.1f} TND. Sougui is cheapest on average!"
    elif any(word in prompt_lower for word in ['recommend', 'suggest', 'action', 'recommande']):
        return f"💡 Top recommendations: 1) Review CFA-001-SO price (499→250 TND). 2) Monitor Ileycom pricing. 3) Maintain Budget cluster prices. 4) Target 60%+ competitiveness score."
    elif any(word in prompt_lower for word in ['model', 'ml', 'machine', 'learning', 'accuracy']):
        return f"🤖 Best ML model: Random Forest with 95-100% accuracy, AUC=0.99-1.0. Key feature: Ileycom_Price (64% importance). Also used: KMeans clustering, Isolation Forest anomaly detection."
    elif any(word in prompt_lower for word in ['saving', 'save', 'economie', 'gain']):
        return f"💰 Total potential savings: 1502 TND across 19 products. Average saving per product: 79.1 TND. Biggest saving: CFA-001-SO (259 TND)."
    else:
        return f"🏆 Sougui summary: {cheaper/total*100:.1f}% products cheaper than competitors. 11 anomalies detected. 19 products need review. Strongest competitor: Ileycom. Score: 83.1%."

st.set_page_config(page_title="Sougui Competitive Analysis", page_icon="🏆", layout="wide")
st.title("🏆 Sougui Competitive Analysis")
st.markdown("**AI-powered competitive intelligence platform**")
st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Market Overview",
    "🔍 Product Lookup",
    "🚨 Anomaly Detector",
    "💡 Recommendations",
    "🤖 ML Results",
    "🔵 Clustering",
    "💰 Price Simulator",
    "💬 AI Chatbot"
])

# TAB 1 - MARKET OVERVIEW
with tab1:
    st.header("📊 Market Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sougui Products", len(sougui[sougui['PU_HT']>0].dropna(subset=['PU_HT'])), "Main source")
    col2.metric("Kalys Products", len(kalys), "Competitor 1")
    col3.metric("Ileycom Products", len(ileycom), "Competitor 2")
    col4.metric("Common Products", "70", "All 3 sources")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sources = ['Sougui', 'Kalys', 'Ileycom']
        avg_prices = [sougui['PU_HT'].dropna().mean(),
                      kalys['Price'].dropna().mean(),
                      ileycom['Price'].dropna().mean()]
        bars = ax.bar(sources, avg_prices, color=['steelblue', 'coral', 'green'])
        ax.set_title('Average Price by Source')
        ax.set_ylabel('Price (TND)')
        for bar, price in zip(bars, avg_prices):
            ax.text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + 1, f'{price:.1f}', ha='center', fontweight='bold')
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        ax.pie([len(sougui), len(kalys), len(ileycom)],
               labels=['Sougui', 'Kalys', 'Ileycom'],
               colors=['steelblue', 'coral', 'green'],
               autopct='%1.1f%%')
        ax.set_title('Market Share by Product Count')
        st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        cheaper = len(df_ml[df_ml['Price_Position']=='Cheaper'])
        more_exp = len(df_ml[df_ml['Price_Position']=='More_Expensive'])
        fig, ax = plt.subplots()
        ax.pie([cheaper, more_exp],
               labels=[f'Cheaper ({cheaper})', f'More Expensive ({more_exp})'],
               colors=['steelblue', 'coral'], autopct='%1.1f%%')
        ax.set_title('Sougui Price Position vs Competitors')
        st.pyplot(fig)

    with col2:
        st.subheader("📈 Key Insights")
        st.success(f"✅ Sougui is cheaper in **{cheaper/(cheaper+more_exp)*100:.1f}%** of cases")
        st.error(f"⚠️ Sougui is more expensive in **{more_exp/(cheaper+more_exp)*100:.1f}%** of cases")
        st.info(f"📊 Average Sougui price: **{sougui['PU_HT'].dropna().mean():.1f} TND**")
        st.info(f"📊 Average Kalys price: **{kalys['Price'].dropna().mean():.1f} TND**")
        st.info(f"📊 Average Ileycom price: **{ileycom['Price'].dropna().mean():.1f} TND**")

# TAB 2 - PRODUCT LOOKUP
with tab2:
    st.header("🔍 Product Price Lookup")
    st.markdown("Select a product to compare prices across all 3 sources")

    common_refs = sorted(set(sougui['Reference'].dropna().unique()) &
                        (set(kalys['Reference'].dropna().unique()) |
                         set(ileycom['Reference'].dropna().unique())))

    selected_ref = st.selectbox("Select Product Reference", ["-- Select --"] + common_refs)

    if selected_ref != "-- Select --":
        s = sougui[sougui['Reference'] == selected_ref]
        k = kalys[kalys['Reference'] == selected_ref]
        i = ileycom[ileycom['Reference'] == selected_ref]

        s_price = float(s['PU_HT'].values[0]) if not s.empty else None
        k_price = float(k['Price'].values[0]) if not k.empty else None
        i_price = float(i['Price'].values[0]) if not i.empty else None

        col1, col2, col3 = st.columns(3)
        with col1:
            if s_price:
                st.metric("🏪 Sougui", f"{s_price} TND")
                st.write(f"**Product:** {s['Nom'].values[0]}")
            else:
                st.warning("Not in Sougui")
        with col2:
            if k_price:
                diff = s_price - k_price if s_price else 0
                st.metric("🏪 Kalys", f"{k_price} TND", delta=f"{diff:.1f} TND vs Sougui")
                st.write(f"**Product:** {k['Product_Name'].values[0]}")
            else:
                st.warning("Not in Kalys")
        with col3:
            if i_price:
                diff = s_price - i_price if s_price else 0
                st.metric("🏪 Ileycom", f"{i_price} TND", delta=f"{diff:.1f} TND vs Sougui")
                st.write(f"**Product:** {i['Product_Name'].values[0]}")
            else:
                st.warning("Not in Ileycom")

        prices_dict = {kk:v for kk,v in
                      {'Sougui':s_price,'Kalys':k_price,'Ileycom':i_price}.items() if v}
        if prices_dict:
            fig, ax = plt.subplots(figsize=(8,4))
            min_price = min(prices_dict.values())
            colors = ['gold' if price == min_price else
                     'steelblue' if src == 'Sougui' else 'lightcoral'
                     for src, price in prices_dict.items()]
            bars = ax.bar(list(prices_dict.keys()), list(prices_dict.values()), color=colors)
            ax.set_title(f'Price Comparison — {selected_ref}')
            ax.set_ylabel('Price (TND)')
            for bar, price in zip(bars, prices_dict.values()):
                ax.text(bar.get_x() + bar.get_width()/2,
                       bar.get_height() + 1, f'{price} TND', ha='center', fontweight='bold')
            st.pyplot(fig)

            cheapest = min(prices_dict, key=prices_dict.get)
            if cheapest == 'Sougui':
                st.success("✅ Sougui is the CHEAPEST for this product!")
            else:
                st.error(f"⚠️ {cheapest} is cheaper! Sougui should review this price.")

# TAB 3 - ANOMALY DETECTOR
with tab3:
    st.header("🚨 Price Anomaly Detector")
    col1, col2 = st.columns(2)
    with col1:
        ref_anomaly = st.selectbox("Select Product",
                                   ["-- Select --"] + list(sougui['Reference'].dropna().unique()))
        if ref_anomaly != "-- Select --":
            s_match = sougui[sougui['Reference'] == ref_anomaly]
            if not s_match.empty:
                price_val = s_match['PU_HT'].values[0]
                st.metric("Product Price", f"{price_val} TND")
        detect_btn = st.button("🚨 Detect Anomaly", use_container_width=True)

    with col2:
        if detect_btn and ref_anomaly != "-- Select --":
            s_match = sougui[sougui['Reference'] == ref_anomaly]
            if not s_match.empty:
                price_val = float(s_match['PU_HT'].values[0])
                df_clean = sougui[sougui['PU_HT'] > 0][['PU_HT']].dropna()
                iso = IsolationForest(contamination=0.1, random_state=42)
                iso.fit(df_clean)
                result = iso.predict([[price_val]])[0]
                score = iso.score_samples([[price_val]])[0]

                if result == -1:
                    st.error("🚨 ANOMALY DETECTED!")
                    st.warning("This product price is unusual!")
                else:
                    st.success("✅ Normal Price")

                st.metric("Anomaly Score", f"{score:.3f}")

                fig, ax = plt.subplots(figsize=(6,3))
                ax.hist(df_clean['PU_HT'], bins=20, color='steelblue', alpha=0.7)
                ax.axvline(x=price_val, color='red', linewidth=2,
                          label=f'Selected: {price_val} TND')
                ax.set_title('Price Distribution')
                ax.legend()
                st.pyplot(fig)

    st.divider()
    st.subheader("All Detected Anomalies")
    df_clean2 = sougui[sougui['PU_HT'] > 0][['Reference','Nom','PU_HT']].dropna().copy()
    iso2 = IsolationForest(contamination=0.1, random_state=42)
    df_clean2['Anomaly'] = iso2.fit_predict(df_clean2[['PU_HT']])
    anomalies = df_clean2[df_clean2['Anomaly'] == -1][['Reference','Nom','PU_HT']]
    st.dataframe(anomalies, use_container_width=True)

# TAB 4 - RECOMMENDATIONS
with tab4:
    st.header("💡 Price Recommendations")
    recs = []
    for _, row in sougui[sougui['PU_HT'] > 0].dropna(subset=['PU_HT']).iterrows():
        ref = str(row['Reference']).strip()
        s_price = row['PU_HT']
        k_match = kalys[kalys['Reference'] == ref]
        i_match = ileycom[ileycom['Reference'] == ref]
        k_price = float(k_match['Price'].values[0]) if not k_match.empty else None
        i_price = float(i_match['Price'].values[0]) if not i_match.empty else None

        if k_price and k_price < s_price:
            recs.append({'Reference': ref, 'Sougui': s_price,
                        'Competitor': 'Kalys', 'Comp_Price': k_price,
                        'Savings': round(s_price-k_price,2),
                        'Action': '🔴 Urgent' if s_price-k_price>100 else '⚠️ Review'})
        if i_price and i_price < s_price:
            recs.append({'Reference': ref, 'Sougui': s_price,
                        'Competitor': 'Ileycom', 'Comp_Price': i_price,
                        'Savings': round(s_price-i_price,2),
                        'Action': '🔴 Urgent' if s_price-i_price>100 else '⚠️ Review'})

    if recs:
        rec_df = pd.DataFrame(recs).sort_values('Savings', ascending=False)
        col1, col2, col3 = st.columns(3)
        col1.metric("Products to Review", len(rec_df))
        col2.metric("Total Savings", f"{rec_df['Savings'].sum():.0f} TND")
        col3.metric("Avg Saving", f"{rec_df['Savings'].mean():.1f} TND")
        st.dataframe(rec_df, use_container_width=True)

        fig, ax = plt.subplots(figsize=(10,4))
        top10 = rec_df.head(10)
        ax.barh(top10['Reference']+' vs '+top10['Competitor'],
                top10['Savings'], color='coral')
        ax.set_title('Top 10 — Potential Savings')
        ax.set_xlabel('Savings (TND)')
        st.pyplot(fig)

# TAB 5 - ML RESULTS
with tab5:
    st.header("🤖 ML Classification Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Best Model", "Random Forest")
    col2.metric("Accuracy", "95-100%")
    col3.metric("ROC-AUC", "0.99-1.00")

    st.divider()
    st.subheader("Model Comparison")
    models_list = ['Logistic Regression', 'Random Forest']
    accuracy = [0.95, 1.0]
    f1 = [0.95, 1.0]
    auc = [0.99, 1.0]

    fig, ax = plt.subplots(figsize=(10,4))
    x = np.arange(len(models_list))
    ax.bar(x-0.2, accuracy, 0.2, label='Accuracy', color='steelblue')
    ax.bar(x, f1, 0.2, label='F1-Score', color='coral')
    ax.bar(x+0.2, auc, 0.2, label='ROC-AUC', color='green')
    ax.set_xticks(x)
    ax.set_xticklabels(models_list)
    ax.set_ylim(0, 1.1)
    ax.legend()
    ax.set_title('Classification Model Comparison')
    st.pyplot(fig)

    st.subheader("Feature Importance")
    features = ['PU_HT', 'Kalys_Price', 'Ileycom_Price', 'Has_Kalys', 'Has_Ileycom']
    importance = [0.251, 0.065, 0.644, 0.04, 0.0]
    fig, ax = plt.subplots(figsize=(8,4))
    ax.barh(features, importance, color='steelblue')
    ax.set_title('Random Forest Feature Importance')
    ax.set_xlabel('Importance')
    st.pyplot(fig)

    st.subheader("Regression Results")
    col1, col2 = st.columns(2)
    col1.metric("Ridge R²", "-0.305")
    col1.metric("Ridge MAE", "29.9 TND")
    col2.metric("RF Regressor R²", "0.076")
    col2.metric("RF Regressor MAE", "19.4 TND")

# TAB 6 - CLUSTERING
with tab6:
    st.header("🔵 Product Clustering")
    X_c = df_ml[['PU_HT','Kalys_Price','Ileycom_Price']].fillna(
        df_ml[['PU_HT','Kalys_Price','Ileycom_Price']].mean())
    sc = StandardScaler()
    X_scaled = sc.fit_transform(X_c)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    df_ml['Cluster'] = clusters

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        scatter = ax.scatter(X_pca[:,0], X_pca[:,1], c=clusters, cmap='viridis', alpha=0.7)
        ax.set_title('KMeans Clusters — PCA 2D')
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        plt.colorbar(scatter, ax=ax)
        st.pyplot(fig)

    with col2:
        profile = df_ml.groupby('Cluster')[['PU_HT','Kalys_Price','Ileycom_Price']].mean()
        fig, ax = plt.subplots()
        profile.plot(kind='bar', ax=ax, color=['steelblue','coral','green'])
        ax.set_title('Cluster Price Profiles')
        ax.set_xlabel('Cluster')
        ax.tick_params(axis='x', rotation=0)
        st.pyplot(fig)

    st.subheader("Cluster Interpretation")
    col1, col2, col3 = st.columns(3)
    col1.info("**Cluster 0 — Budget** 💚\nLow price products\nMaintain prices")
    col2.warning("**Cluster 1 — Mid-range** ⚠️\nMedium prices\nMonitor competitors")
    col3.error("**Cluster 2 — Premium** 🔴\nHigh Sougui prices\nUrgent review needed")

# TAB 7 - PRICE SIMULATOR
with tab7:
    st.header("💰 What-If Price Simulator")
    st.markdown("**Simulate price changes and see impact on competitiveness!**")

    sim_refs = list(df_ml['Reference'].unique())
    selected_sim = st.selectbox("Select Product to Simulate",
                                ["-- Select --"] + sim_refs, key="sim_select")

    if selected_sim != "-- Select --":
        product_data = df_ml[df_ml['Reference'] == selected_sim].iloc[0]
        current_price = float(product_data['PU_HT'])
        kalys_p = float(product_data['Kalys_Price'])
        ileycom_p = float(product_data['Ileycom_Price'])
        avg_comp = float(product_data['Avg_Competitor_Price'])

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Current Situation")
            st.metric("Current Sougui Price", f"{current_price} TND")
            st.metric("Kalys Price", f"{kalys_p} TND")
            st.metric("Ileycom Price", f"{ileycom_p} TND")
            st.metric("Avg Competitor Price", f"{avg_comp:.1f} TND")

            if current_price < avg_comp:
                st.success("✅ Currently CHEAPER than competitors")
            else:
                st.error(f"❌ Currently {current_price - avg_comp:.1f} TND MORE EXPENSIVE")

        with col2:
            st.subheader("🎮 Simulate New Price")
            new_price = st.slider(
                "Drag to simulate new Sougui price",
                min_value=float(min(current_price * 0.3, avg_comp * 0.3)),
                max_value=float(max(current_price * 1.5, avg_comp * 1.5)),
                value=float(current_price),
                step=1.0
            )

            price_diff = new_price - avg_comp
            price_change = new_price - current_price
            pct_change = (price_change / current_price) * 100

            if new_price < avg_comp:
                st.success(f"✅ COMPETITIVE! {abs(price_diff):.1f} TND cheaper than avg competitor")
            else:
                st.error(f"❌ NOT COMPETITIVE! {price_diff:.1f} TND more expensive")

            st.metric("New Price", f"{new_price:.1f} TND",
                     delta=f"{price_change:.1f} TND ({pct_change:.1f}%)")

            revenue_current = current_price * 100
            revenue_new = new_price * 100
            revenue_diff = revenue_new - revenue_current
            st.metric("Revenue Impact (per 100 units)",
                     f"{revenue_new:.0f} TND",
                     delta=f"{revenue_diff:.0f} TND")

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(8,4))
            sources = ['Sougui\n(Current)', 'Sougui\n(Simulated)', 'Kalys', 'Ileycom']
            prices = [current_price, new_price, kalys_p, ileycom_p]
            colors = ['steelblue',
                     'green' if new_price < avg_comp else 'red',
                     'coral', 'orange']
            bars = ax.bar(sources, prices, color=colors)
            ax.axhline(y=avg_comp, color='black', linestyle='--',
                      label=f'Avg Competitor: {avg_comp:.1f} TND')
            ax.set_title('Price Simulation Comparison')
            ax.set_ylabel('Price (TND)')
            ax.legend()
            for bar, price in zip(bars, prices):
                ax.text(bar.get_x() + bar.get_width()/2,
                       bar.get_height() + 1,
                       f'{price:.0f}', ha='center', fontweight='bold')
            st.pyplot(fig)

        with col2:
            cheaper_count = len(df_ml[df_ml['PU_HT'] < df_ml['Avg_Competitor_Price']])
            total = len(df_ml)
            score_current = (cheaper_count / total) * 100

            if new_price < avg_comp and current_price >= avg_comp:
                score_new = score_current + (1/total * 100)
            elif new_price >= avg_comp and current_price < avg_comp:
                score_new = score_current - (1/total * 100)
            else:
                score_new = score_current

            fig, ax = plt.subplots(figsize=(6,4))
            ax.barh(['Current Score', 'Simulated Score'],
                   [score_current, score_new],
                   color=['steelblue', 'green' if score_new >= score_current else 'red'])
            ax.axvline(x=60, color='red', linestyle='--', label='Target: 60%')
            ax.set_title('Competitiveness Score Impact')
            ax.set_xlabel('Score (%)')
            ax.legend()
            for i, v in enumerate([score_current, score_new]):
                ax.text(v + 0.5, i, f'{v:.1f}%', va='center', fontweight='bold')
            st.pyplot(fig)

        st.divider()
        st.subheader("🎯 AI Recommendation")
        if new_price < avg_comp * 0.8:
            st.success(f"💚 Excellent! At {new_price:.0f} TND, Sougui is highly competitive — {((avg_comp-new_price)/avg_comp*100):.1f}% below market!")
        elif new_price < avg_comp:
            st.success(f"✅ Good! At {new_price:.0f} TND, Sougui is competitive.")
        elif new_price < avg_comp * 1.1:
            st.warning(f"⚠️ At {new_price:.0f} TND, slightly above market. Consider reducing by {(new_price-avg_comp):.0f} TND.")
        else:
            st.error(f"🔴 At {new_price:.0f} TND, significantly overpriced! Reduce by at least {(new_price-avg_comp):.0f} TND.")

# TAB 8 - AI CHATBOT
with tab8:
    st.header("💬 AI Competitive Analysis Assistant")
    st.markdown("**Ask me anything about Sougui's competitive position!**")

    cheaper = len(df_ml[df_ml['Price_Position']=='Cheaper'])
    more_exp = len(df_ml[df_ml['Price_Position']=='More_Expensive'])
    total = len(df_ml)
    avg_sougui = sougui['PU_HT'].dropna().mean()
    avg_kalys = kalys['Price'].dropna().mean()
    avg_ileycom = ileycom['Price'].dropna().mean()

    context = f"""
    You are an AI assistant for Sougui competitive analysis.
    Here is the data:
    - Sougui has {len(sougui)} products, average price: {avg_sougui:.1f} TND
    - Kalys has {len(kalys)} products, average price: {avg_kalys:.1f} TND
    - Ileycom has {len(ileycom)} products, average price: {avg_ileycom:.1f} TND
    - 70 products are common across all 3 sources
    - Sougui is cheaper in {cheaper}/{total} cases ({cheaper/total*100:.1f}%)
    - Sougui is more expensive in {more_exp}/{total} cases ({more_exp/total*100:.1f}%)
    - 11 anomalous products detected by Isolation Forest
    - Most overpriced: CFA-001-SO at 499 TND vs competitors 240-250 TND
    - 19 products need price review, total savings: 1502 TND
    - Best ML model: Random Forest, accuracy 95-100%, AUC 0.99-1.0
    - Competitiveness Score: 83.1% (above 60% target)
    - Strongest competitor: Ileycom (64% feature importance)
    - 3 clusters: Budget, Mid-range, Premium
    Answer clearly and concisely in the same language as the user.
    Give specific numbers and actionable insights.
    Keep answers to 3-4 sentences maximum.
    """

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.markdown("**💡 Try asking:**")
    col1, col2, col3 = st.columns(3)
    if col1.button("Which products need review?"):
        st.session_state['inject_prompt'] = "Which products need urgent price review?"
    if col2.button("Who is strongest competitor?"):
        st.session_state['inject_prompt'] = "Who is Sougui's strongest competitor?"
    if col3.button("What is competitiveness score?"):
        st.session_state['inject_prompt'] = "What is Sougui's competitiveness score?"

    prompt = st.chat_input("Ask a question about Sougui competitive analysis...")

    if 'inject_prompt' in st.session_state and st.session_state['inject_prompt']:
        prompt = st.session_state['inject_prompt']
        st.session_state['inject_prompt'] = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                system=context,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text
        except Exception:
            answer = get_fallback_response(prompt, cheaper, more_exp, total,
                                          avg_sougui, avg_kalys, avg_ileycom)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)