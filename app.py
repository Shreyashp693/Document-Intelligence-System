import streamlit as st
import pandas as pd
import pdfplumber
from textblob import TextBlob

st.set_page_config(page_title="Document Intelligence System")

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def correct_query(query):
    return str(TextBlob(query).correct())

def detect_intent(query):
    query = query.lower()
    if "summarize" in query or "summary" in query:
        return "Summary"
    elif "count" in query or "how many" in query:
        return "Count"
    elif "top" in query or "highest" in query:
        return "Sorting"
    elif "average" in query or "sum" in query or "total" in query:
        return "Aggregation"
    elif "find" in query or "search" in query:
        return "Search"
    elif "show" in query or "list" in query:
        return "Filter"
    return "Unknown"

def summarize_text(text):
    words = text.split()
    return text if len(words) <= 100 else " ".join(words[:100]) + "..."

def search_dataframe(df, keyword):
    mask = df.astype(str).apply(
        lambda row: row.str.contains(keyword, case=False).any(),
        axis=1
    )
    return df[mask]

st.title("Document Intelligence System")

uploaded_file = st.file_uploader("Upload PDF, Excel, or CSV", type=["pdf","xlsx","csv"])
query = st.text_input("Enter your query")

if uploaded_file and query:
    original_query = query
    corrected_query = correct_query(query)
    intent = detect_intent(corrected_query)

    st.write(f"**File Type:** {uploaded_file.name.split('.')[-1].upper()}")
    st.write(f"**Original Query:** {original_query}")
    st.write(f"**Corrected Query:** {corrected_query}")
    st.write(f"**Detected Intent:** {intent}")

    if uploaded_file.name.endswith(".pdf"):
        text = read_pdf(uploaded_file)
        result = summarize_text(text) if intent == "Summary" else "Intent not supported for PDF."
        st.write(result)
    else:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)

        if intent in ["Filter", "Search"]:
            keyword = corrected_query.split()[-1]
            st.dataframe(search_dataframe(df, keyword))
        elif intent == "Count":
            st.write(f"Total Rows: {len(df)}")
        elif intent == "Sorting":
            nums = df.select_dtypes(include="number").columns
            if len(nums):
                st.dataframe(df.sort_values(by=nums[0], ascending=False).head(5))
        elif intent == "Aggregation":
            nums = df.select_dtypes(include="number").columns
            if len(nums):
                st.write(f"Total = {df[nums[0]].sum()}")
