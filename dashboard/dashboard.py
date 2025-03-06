import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv", parse_dates=["order_purchase_timestamp", 
                                                    "order_delivered_customer_date", 
                                                    "order_estimated_delivery_date"])
    return df

df = load_data()

# Sidebar untuk filter
st.sidebar.header("Filter Data")
selected_category = st.sidebar.selectbox("Pilih Kategori Produk", ["Semua"] + list(df["product_category_name"].dropna().unique()))
selected_payment = st.sidebar.selectbox("Pilih Metode Pembayaran", ["Semua"] + list(df["payment_type"].dropna().unique()))

# Filter data
if selected_category != "Semua":
    df = df[df["product_category_name"] == selected_category]
if selected_payment != "Semua":
    df = df[df["payment_type"] == selected_payment]

# **1. Ringkasan Data**
st.title("📊 E-Commerce Dashboard")
st.write("Dashboard ini menampilkan analisis dari data transaksi e-commerce.")

col1, col2, col3 = st.columns(3)
col1.metric("Total Pesanan", df["order_id"].nunique())
col2.metric("Total Penjualan", f"Rp {df['payment_value'].sum():,.0f}")
col3.metric("Rata-rata Keterlambatan", f"{df['delivery_delay'].mean():.2f} hari")

# **2. Faktor Keterlambatan Pengiriman**
st.subheader("📦 Faktor Keterlambatan Pengiriman")

# Grafik 1: Kategori Produk dengan Keterlambatan Tertinggi
delay_factors = df.groupby("product_category_name")["delivery_delay"].mean().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=delay_factors.values, y=delay_factors.index, palette="coolwarm", ax=ax)
ax.set_xlabel("Rata-rata Keterlambatan (hari)")
ax.set_ylabel("Kategori Produk")
st.pyplot(fig)

# Grafik 2: Distribusi Keterlambatan Pengiriman
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df["delivery_delay"].dropna(), bins=30, kde=True, color="blue")
ax.set_xlabel("Keterlambatan (Hari)")
ax.set_ylabel("Jumlah Pesanan")
ax.set_title("Distribusi Keterlambatan Pengiriman")
st.pyplot(fig)

# **3. Pengaruh Metode Pembayaran terhadap Nilai Transaksi**
st.subheader("💳 Pengaruh Metode Pembayaran terhadap Nilai Transaksi")
payment_avg = df.groupby("payment_type")["payment_value"].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=payment_avg.index, y=payment_avg.values, palette="viridis", ax=ax)
ax.set_ylabel("Rata-rata Nilai Transaksi (Rp)")
st.pyplot(fig)

# **4. Analisis RFM**
st.subheader("🛍️ Analisis RFM (Recency, Frequency, Monetary)")
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sns.histplot(df["Recency"], bins=30, kde=True, ax=axes[0], color="blue")
sns.histplot(df["Frequency"], bins=30, kde=True, ax=axes[1], color="green")
sns.histplot(df["Monetary"], bins=30, kde=True, ax=axes[2], color="orange")
axes[0].set_title("Recency (Hari sejak terakhir beli)")
axes[1].set_title("Frequency (Jumlah Pesanan)")
axes[2].set_title("Monetary (Total Nilai Transaksi)")
plt.tight_layout()
st.pyplot(fig)

# **5. Pola Geografis dalam Frekuensi dan Nilai Pesanan**
st.subheader("🌍 Pola Geografis dalam Frekuensi dan Nilai Pesanan")

# Gunakan visualisasi dari analisis sebelumnya: Bar Chart Order Volume per Zip Code
zip_order_counts = df["customer_zip_code_prefix"].value_counts().head(15)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=zip_order_counts.values, y=zip_order_counts.index, palette="plasma", ax=ax)
ax.set_xlabel("Jumlah Pesanan")
ax.set_ylabel("Zip Code")
ax.set_title("Order Volume berdasarkan Zip Code")
st.pyplot(fig)

# **6. Pengelompokan Kategori Produk berdasarkan Harga & Volume Penjualan**
st.subheader("🛒 Kategori Produk berdasarkan Harga & Volume Penjualan")

# Urutkan kategori berdasarkan total sales agar kategori populer lebih terlihat
top_categories = df.groupby("product_category_name").agg(
    avg_price=("avg_price", "mean"),
    total_sales=("total_sales", "sum")
).sort_values(by="total_sales", ascending=False).head(10).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))

# Plot dengan hue sebagai warna berbeda, tetapi titiknya lebih transparan
sns.scatterplot(data=top_categories, 
                x="avg_price", 
                y="total_sales", 
                hue="product_category_name", 
                palette="tab10", 
                s=100, 
                edgecolor="black", 
                alpha=0.8, 
                ax=ax)

# Tambahkan label di sebelah titik-titik untuk kategori utama
for i, row in top_categories.iterrows():
    ax.annotate(row["product_category_name"], 
                (row["avg_price"], row["total_sales"]), 
                textcoords="offset points", 
                xytext=(5,5), 
                ha="right", 
                fontsize=8, 
                color="black")

ax.set_xlabel("Rata-rata Harga Produk")
ax.set_ylabel("Total Volume Penjualan")
ax.set_title("Hubungan antara Harga dan Volume Penjualan per Kategori Produk")

# Tampilkan legend secara terpisah agar tidak mengganggu grafik
plt.legend(title="Kategori Produk", bbox_to_anchor=(1.05, 1), loc="upper left")

st.pyplot(fig)

st.write("🚀 Dashboard ini dibuat berdasarkan dataset hasil analisis.")
