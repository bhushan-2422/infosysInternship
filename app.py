import streamlit as st
import pandas as pd
from datetime import datetime

from preprocess_data import process_data
from rating_based_recommendation import get_top_rated_items
from content_based_filtering import content_based_recommendation
from collaborative_based_filtering import collaborative_filtering_recommendations


# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="MyCart",
    page_icon="🛒",
    layout="wide"
)

# ===================== GLOBAL CSS =====================
st.markdown("""
<style>
.product-card {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px;
    height: 460px;
    background: black;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.product-img {
    height: 180px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.product-img img {
    max-height: 100%;
    max-width: 100%;
    object-fit: contain;
}

.card-footer {
    margin-top: auto;
}

.sidebar-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #10b981;
}
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user_id" not in st.session_state:
    st.session_state.user_id = 0

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "data" not in st.session_state:
    with st.spinner("Loading product data..."):
        raw = pd.read_csv("clean_data.csv")
        st.session_state.data = process_data(raw)

data = st.session_state.data


# ===================== HELPERS =====================
def add_to_search_history(query):
    if query.strip():
        if not any(q["query"].lower() == query.lower() for q in st.session_state.search_history):
            st.session_state.search_history.append({
                "query": query,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })


def display_product_grid(df):
    if df.empty:
        st.info("No products found")
        return

    for i in range(0, len(df), 4):
        cols = st.columns(4)

        for col, (_, p) in zip(cols, df.iloc[i:i+4].iterrows()):
            with col:
                image = str(p["ImageURL"]).split("|")[0]

                st.markdown(f"""
                <div class="product-card">
                    <div class="product-img">
                        <img src="{image}" />
                    </div>
                    <div>
                        <strong>{p["Name"][:60]}</strong><br/>
                        <small>{p["Brand"]}</small><br/>
                        ⭐ {p["Rating"]}/5
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.button("🛒 Add to Cart", key=f"cart_{p['Name']}")


# ===================== SIDEBAR =====================
def sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>&lt;MyCart/&gt;</div>", unsafe_allow_html=True)
        st.markdown(f"👤 **User ID:** `{st.session_state.user_id}`")
        st.markdown("---")

        if st.session_state.search_history:
            st.markdown("### 🕐 Search History")
            for item in reversed(st.session_state.search_history[-8:]):
                if st.button(item["query"], use_container_width=True):
                    st.session_state.selected_search = item["query"]
                    st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.page = "login"
            st.session_state.user_id = 0
            st.session_state.search_history = []
            st.rerun()


# ===================== LOGIN PAGE =====================
def login_page():
    st.markdown("<h1 style='text-align:center;'>🛒 MyCart Login</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user_id = st.text_input("User ID", value="0")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary", use_container_width=True):
            try:
                st.session_state.user_id = int(user_id)
                st.session_state.page = "home"
                st.rerun()
            except:
                st.error("User ID must be a number")


# ===================== HOME PAGE =====================
def home_page():
    sidebar()

    st.title("🛒 Product Recommendations")

    col1, col2 = st.columns([4,1])
    with col1:
        default = st.session_state.get("selected_search", "")
        query = st.text_input("Search product", value=default)
        st.session_state.pop("selected_search", None)

    with col2:
        search = st.button("Search", type="primary", use_container_width=True)

    st.markdown("---")

    st.subheader("⭐ Highly Rated Products")
    top_df = get_top_rated_items(data, top_n=12)
    display_product_grid(top_df)

    if search and query.strip():
        add_to_search_history(query)

        st.subheader("🎯 Similar Products")
        sim_df = content_based_recommendation(data, query, top_n=12)
        display_product_grid(sim_df)

        if st.session_state.user_id != 0:
            st.subheader("👥 Recommended for You")
            collab_df = collaborative_filtering_recommendations(
                data, st.session_state.user_id, top_n=12
            )
            display_product_grid(collab_df)


# ===================== ROUTER =====================
if st.session_state.page == "login":
    login_page()
else:
    home_page()
