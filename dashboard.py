
import streamlit as st
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
import altair as alt
import matplotlib.pyplot as plt
from collections import Counter

# ===== الاتصال بقاعدة MongoDB =====
client = MongoClient("mongodb+srv://mohamedalibadawypr:AQpmE96i6p7O7Zpj@worklocate.ljup3kj.mongodb.net/workLocate?retryWrites=true")  # غيّر حسب حالتك
db = client["workLocate"]  # 👈 غيّر لاسم قاعدة البيانات
collection = db["workingspaces"]  # 👈 غيّر لاسم الـ collection

# ===== تنظيف البيانات =====
def clean_document(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, list):
            doc[key] = [str(item) if isinstance(item, ObjectId) else item for item in value]
        elif isinstance(value, dict):
            doc[key] = clean_document(value)
    return doc

raw_data = list(collection.find())
cleaned_data = [clean_document(doc) for doc in raw_data]
df = pd.DataFrame(cleaned_data)

# ===== معالجة الإحداثيات =====
df["lat"] = df["location"].apply(lambda x: x["coordinates"][1] if isinstance(x, dict) else None)
df["lon"] = df["location"].apply(lambda x: x["coordinates"][0] if isinstance(x, dict) else None)

# ===== عرض العنوان الرئيسي =====
st.title("📊 Workspaces Dashboard")

# ===== فلترة بالتقييم =====
st.subheader("🔢 فلترة حسب التقييم")
min_rating, max_rating = st.slider("اختر نطاق التقييم:", 0.0, 5.0, (0.0, 5.0), step=0.1)
df = df[df["averageRating"].between(min_rating, max_rating)]

# ===== البحث بالاسم أو العنوان =====
st.subheader("🔍 البحث")
search_text = st.text_input("اكتب اسم أو عنوان المكان:")
if search_text:
    df = df[df["name"].str.contains(search_text, case=False, na=False) |
            df["address"].str.contains(search_text, case=False, na=False)]

st.write(f"عدد الأماكن المعروضة: {len(df)}")

# ===== جدول البيانات =====
st.subheader("📋 قائمة الأماكن")
st.dataframe(df[["name", "address", "averageRating", "roomCounter"]])

# ===== خريطة المواقع =====
st.subheader("📍 خريطة الأماكن")
st.map(df[["lat", "lon"]].dropna())

# ===== رسم بياني للتقييمات =====
st.subheader("⭐ متوسط التقييمات لكل مكان")
rating_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('name:N', sort='-y'),
    y='averageRating:Q',
    tooltip=['name', 'averageRating']
).properties(width=700, height=400)
st.altair_chart(rating_chart)

# ===== فلترة حسب الخدمات =====
df["amenities"] = df["amenities"].apply(lambda x: [str(i) for i in x] if isinstance(x, list) else [])
all_amenities = sorted(set([item for sublist in df["amenities"] for item in sublist]))
selected_amenity = st.selectbox("🔌 اختر خدمة:", [""] + all_amenities)

if selected_amenity:
    filtered_df = df[df["amenities"].apply(lambda x: selected_amenity in x)]
    st.write(f"عدد الأماكن التي توفر '{selected_amenity}': {len(filtered_df)}")
    st.dataframe(filtered_df[["name", "address", "averageRating"]])

# ===== رسم Pie Chart للخدمات =====
st.subheader("🎯 أكثر الخدمات استخدامًا (Top 10)")
all_amenities_flat = [item for sublist in df["amenities"] for item in sublist]
amenity_counts = Counter(all_amenities_flat)
top_amenities = amenity_counts.most_common(10)

if top_amenities:
    labels, values = zip(*top_amenities)
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)
else:
    st.write("لا توجد بيانات كافية لعرض مخطط الخدمات.")
    
    
    
    
    
c1,c2,c3=st.columns((3,3,3))
with c1 :
    st.write("c1")
    
with c2 :
    st.write("c2")
with c3 :
    st.write("c3")

