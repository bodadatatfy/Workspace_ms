
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


df = df.drop(columns=['question', 'timestamp', 'response', 'ownerId', 'reviews', '__v'])
df['City'] = df['address'].str.split(',').str[-2].str.strip()



# ===== فلترة بالتقييم =====

st.sidebar.header(" Workspaces Dashboard  ")
st.sidebar.image("photo.jpg")
st.sidebar.subheader(" Filter by rating ")
min_rating, max_rating = st.sidebar.slider("Choose the evaluation range : " ,1.0, 5.0, (1.0, 5.0), step=0.1)
df = df[df["averageRating"].between(min_rating, max_rating)]

# ===== البحث بالاسم أو العنوان =====
st.sidebar.subheader(" Research  🔍 ")
search_text = st.sidebar.text_input("Enter the name or title of the place:")
if search_text:
    df = df[df["name"].str.contains(search_text, case=False, na=False) |
            df["address"].str.contains(search_text, case=False, na=False)]
  
    
    
    #BodyDashboard
    
    # ===== عرض العنوان الرئيسي =====
st.title(" Workspaces Dashboard 📊 ")

  #row1
col1,col2,col3,col4=st.columns(4)
st.write("")
st.write("")
st.write("")

col1.metric("Max Of RoomCounter",df['roomCounter'].max(),)
col2.metric("Min Of RoomCounter",df['roomCounter'].min())
col3.metric("WorkSpace Counter",df['roomCounter'].count())
col4.metric("City Counter",df['City'].nunique()
)


st.write(f"Number of displayed places: {len(df)}")

# ===== جدول البيانات =====
st.subheader("List of places 📋 ")
st.dataframe(df[["name", "address", "averageRating", "roomCounter","amenities"]])



# ===== رسم بياني للتقييمات =====
st.subheader("⭐ Average ratings for each place")
rating_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('name:N', sort='-y'),
    y='averageRating:Q',
    tooltip=['name', 'averageRating']
).properties(width=700, height=400)
st.altair_chart(rating_chart)



# ===== رسم Pie Chart للخدمات =====
st.subheader("🎯 Most used services (Top 10)")
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
    st.write("There is not enough data to display the service chart..")
