import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize
import gdown

file_id = '1unNEL3twDD3-tiUNWL1FrQe60nl0LA2-'  # Βάλε εδώ το δικό σου ID
url = f'https://drive.google.com/uc?id={file_id}'

output = "Retail_Transactions_Dataset.csv"
gdown.download(url, output, quiet=False)

# Διάβασε το CSV
df = pd.read_csv(output)

# Τσέκαρε τις στήλες
print(df.columns.tolist())


# === 2. Ρυθμίσεις του Streamlit
st.set_page_config(page_title="Market Basket Analysis", layout="wide")

# === 3. Τίτλος και υπότιτλος
st.markdown("<h1 style='text-align: center; font-size: 42px; font-style: italic;'>🛒 Market Basket Analysis</h1>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

# === 4. Προσθήκη τίτλου και υπότιτλου στην sidebar
st.sidebar.markdown("<h2 style='text-align: center;'>👋 Welcome to my Dashboard</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<h4 style='text-align: center;'>Don't forget to use the filters!</h4>", unsafe_allow_html=True)

# === Sidebar - Filters
st.sidebar.header("🔍 Filters")
customer_categories = ["All"] + sorted(df['Customer_Category'].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Customer Category", customer_categories)

selected_seasons = st.sidebar.multiselect("Select Seasons", options=df['Season'].unique(), default=df['Season'].unique())
min_items, max_items = int(df["Total_Items"].min()), int(df["Total_Items"].max())
basket_range = st.sidebar.slider("Select Basket Size", min_value=min_items, max_value=max_items, value=(min_items, max_items))

# === Adding the new questions to the sidebar
st.sidebar.markdown("### Can you help me answer the following Questions?")
st.sidebar.markdown("- What is the most sold product overall?")
st.sidebar.markdown("- Which products are in the top 10 most sold list?")
st.sidebar.markdown("- What is the most common range of total items purchased per transaction?")
st.sidebar.markdown("- What is the average number of items purchased per transaction?")
st.sidebar.markdown("- How does the distribution of total items vary across customer categories?")
st.sidebar.markdown("- Is there a specific range where most transactions occur, regardless of customer category?")
st.sidebar.markdown("- Which year had the lowest overall total cost across all seasons?")
st.sidebar.markdown("- During which season and year did the total cost reach its highest point?")

# === Εφαρμογή φίλτρων
filtered_df = df[
    (df['Season'].isin(selected_seasons)) &
    (df['Total_Items'] >= basket_range[0]) &
    (df['Total_Items'] <= basket_range[1])
]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Customer_Category"] == selected_category]

# === Διάγραμμα 1
st.markdown("## 🥇 Top 10 Most Sold Products", unsafe_allow_html=True)

# Χρήση δύο στηλών με την αριστερή στήλη για τις ερωτήσεις
col1, col2 = st.columns([1, 3])

with col1:
    # Τοποθετούμε τις ερωτήσεις με λιγότερο κενό
    st.markdown("<div style='margin-top: 75px;'></div>", unsafe_allow_html=True)  # Μειωμένο κενό
    st.markdown("### 📌 Questions:")
    st.markdown("- What is the most sold product overall?")
    st.markdown("- Which products are in the top 10 most sold list?")

with col2:
    top_products = (
        filtered_df.groupby("Product", as_index=False)["Total_Items"]
        .sum()
        .sort_values(by="Total_Items", ascending=False)
        .head(10)
    )

    x_positions = np.linspace(1, 10, 10)
    y_positions = np.random.uniform(6, 9, 10)
    sizes = top_products["Total_Items"]
    scaled_sizes = sizes / sizes.max() * 2500
    colors = plt.cm.tab10(np.linspace(0, 1, len(top_products)))

    # Αύξηση πλάτους και ύψους του γραφήματος
    fig, ax = plt.subplots(figsize=(15, 7))  # Αύξηση πλάτους και ύψους
    ax.scatter(x_positions, y_positions, s=scaled_sizes * 3.5, c=colors, alpha=0.85, edgecolors='black')

    for i, product in enumerate(top_products["Product"]):
        ax.text(x_positions[i], y_positions[i], f"{product}\n{top_products['Total_Items'].iloc[i]}",
                ha='center', va='center', fontsize=8, color='white', weight='bold')

    ax.set_title("Top 10 Most Sold Products", fontsize=14, weight='bold', color='#2980B9')
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

# === Διάγραμμα 2
st.markdown("## 🧺 Total Products Sold by Basket Size Range", unsafe_allow_html=True)

# Ερωτήσεις για το Διάγραμμα 2
st.markdown("<div style='margin-top: 75px;'></div>", unsafe_allow_html=True)  # Μειωμένο κενό πριν τις ερωτήσεις
st.markdown("### 📌 Questions:")
st.markdown("- What is the most common range of total items purchased per transaction?")
st.markdown("- What is the average number of items purchased per transaction?")
st.markdown("- How does the distribution of total items vary across customer categories?")
st.markdown("- Is there a specific range where most transactions occur, regardless of customer category?")

bin_size = 2
bins = np.arange(0, df['Total_Items'].max() + bin_size, bin_size)
filtered_df['Bins'] = pd.cut(filtered_df['Total_Items'], bins=bins, right=False)
bin_totals = filtered_df.groupby('Bins')['Total_Items'].sum()

average = bin_totals.mean()
norm = Normalize(vmin=bin_totals.min(), vmax=bin_totals.max())
colors = [cm.Blues(norm(value)) for value in bin_totals]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(bin_totals.index.astype(str), bin_totals, color=colors, edgecolor='black')
ax.axhline(average, color='black', linestyle='dashed', linewidth=2, label=f'Average: {average:,.2f}'.replace(',', '.'))

for bar in bars:
    height = int(bar.get_height())
    label = f'{height:,}'.replace(',', '.')
    ax.text(bar.get_x() + bar.get_width() / 2, height + 2, label, ha='center', va='bottom', fontsize=8, color='black', weight='bold')

ax.set_title("Total Products Sold by Basket Size Range", fontsize=14, color='#2980B9')
ax.set_xlabel("Basket Size Range (Total Items)", fontsize=10)
ax.set_ylabel("Total Products Sold", fontsize=10)
ax.set_xticks(np.arange(len(bin_totals.index)))
ax.set_xticklabels(bin_totals.index.astype(str), rotation=45)
ax.legend()
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
st.pyplot(fig)

st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

# === Διάγραμμα 3
st.markdown("## 📈 Total Sales Cost by Season and Year", unsafe_allow_html=True)

# Ερωτήσεις για το Διάγραμμα 3
st.markdown("<div style='margin-top: 75px;'></div>", unsafe_allow_html=True)  # Μειωμένο κενό πριν τις ερωτήσεις
st.markdown("### 📌 Questions:")
st.markdown("- Which year had the lowest overall total cost across all seasons?")
st.markdown("- During which season and year did the total cost reach its highest point?")

filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
filtered_df['Year'] = filtered_df['Date'].dt.year
grouped = (
    filtered_df.groupby(['Season', 'Year'])['Total_Cost']
    .sum()
    .reset_index()
    .round(0)
    .astype({'Total_Cost': int})
)

seasons = ['Fall', 'Spring', 'Summer', 'Winter']
colors = {'Fall': 'royalblue', 'Spring': 'darkorange', 'Summer': 'crimson', 'Winter': 'teal'}
fig, axes = plt.subplots(1, 4, figsize=(20, 5), sharey=True)
all_years = sorted(filtered_df['Year'].unique())

for i, season in enumerate(seasons):
    ax = axes[i]
    season_data = grouped[grouped['Season'] == season]
    ax.plot(season_data['Year'], season_data['Total_Cost'], marker='o', color=colors[season])

    for _, row in season_data.iterrows():
        ax.text(row['Year'], row['Total_Cost'] + 3000, f"{row['Total_Cost']:,}", ha='center', fontsize=8)

    ax.set_title(season, fontsize=12, color=colors[season])
    ax.set_xlabel("Year")
    ax.set_xticks(all_years)
    ax.set_xticklabels(all_years, rotation=0)

    if i == 0:
        ax.set_ylabel("Total Sales Cost")
    ax.grid(True, linestyle='--', alpha=0.5)

plt.suptitle("Total Sales Cost by Season and Year", fontsize=15, weight='bold', color='#2980B9')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
st.pyplot(fig)