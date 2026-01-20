import streamlit as st
import pandas as pd
from datetime import datetime

from preprocess_data import process_data
from rating_based_recommendation import get_top_rated_items
from content_based_filtering import content_based_recommendation
from collaborative_based_filtering import collaborative_filtering_recommendations

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MyCart - Product Recommendations",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>
    .main-logo {
        font-size: 2rem;
        font-weight: 700;
        color: #10b981;
        font-family: 'Monaco', monospace;
        margin-bottom: 1rem;
    }
    .product-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        background: white;
        transition: transform 0.2s;
        height: 100%;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        
    }
    .search-history-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background: #f3f4f6;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
    }
    .search-history-item:hover {
        background: #e5e7eb;
    }
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZE SESSION STATE ----------------
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'data' not in st.session_state:
    with st.spinner('Loading product data...'):
        raw_data = pd.read_csv("clean_data.csv")
        st.session_state.data = process_data(raw_data)

data = st.session_state.data

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown('<div class="main-logo">&lt;MyCart/&gt;</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    user_id = st.text_input(
        "👤 User ID",
        value="0",
        help="Enter your User ID or 0 for Guest/New User",
        placeholder="0"
    )
    
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 0
        st.warning("Invalid User ID. Using Guest mode (0)")
    
    # Display search history
    if st.session_state.search_history:
        st.markdown("---")
        st.markdown("### 🕐 Recent Searches")
        
        for i, search_item in enumerate(reversed(st.session_state.search_history[-10:])):
            if st.button(
                f"🔍 {search_item['query'][:25]}{'...' if len(search_item['query']) > 25 else ''}",
                key=f"history_{i}",
                help=f"Searched on {search_item['timestamp']}"
            ):
                st.session_state.selected_search = search_item['query']
                st.rerun()

# ---------------- HELPER FUNCTIONS ----------------
def add_to_search_history(query):
    """Add search query to history with timestamp"""
    if query and query.strip():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        # Avoid duplicates
        if not any(item['query'].lower() == query.lower() for item in st.session_state.search_history):
            st.session_state.search_history.append({
                'query': query.strip(),
                'timestamp': timestamp
            })

def get_rating_based_recommendations(top_n=16):
    """Get top rated products"""
    try:
        result = get_top_rated_items(data, top_n=top_n)
        return pd.DataFrame(result) if not isinstance(result, pd.DataFrame) else result
    except Exception as e:
        st.error(f"Error fetching top rated products: {str(e)}")
        return pd.DataFrame()

def get_content_based_recommendations(item_name, top_n=16):
    """Get content based recommendations"""
    try:
        result = content_based_recommendation(data, item_name, top_n=top_n)
        return pd.DataFrame(result) if not isinstance(result, pd.DataFrame) else result
    except Exception as e:
        st.error(f"Error fetching content recommendations: {str(e)}")
        return pd.DataFrame()

def get_collaborative_recommendations(user_id, top_n=16):
    """Get collaborative filtering recommendations"""
    try:
        result = collaborative_filtering_recommendations(data, user_id, top_n=top_n)
        return pd.DataFrame(result) if not isinstance(result, pd.DataFrame) else result
    except Exception as e:
        st.error(f"Error fetching collaborative recommendations: {str(e)}")
        return pd.DataFrame()

def display_product_grid(df, columns=4):
    """Display products in a responsive grid layout"""
    if df.empty:
        st.info("🔍 No products found matching your criteria")
        return
    
    # Ensure required columns exist
    required_cols = ['Name', 'Brand', 'Rating', 'ImageURL']
    if not all(col in df.columns for col in required_cols):
        st.error("Product data is missing required fields")
        return
    
    rows = [df.iloc[i:i+columns] for i in range(0, len(df), columns)]
    
    for row_data in rows:
        cols = st.columns(columns)
        
        for idx, (col, (_, product)) in enumerate(zip(cols, row_data.iterrows())):
            with col:
                # Get first image from pipe-separated URLs
                image_url = str(product['ImageURL']).split('|')[0].strip()
                
                # Display image
                try:
                    st.image(image_url, use_container_width=True)
                except:
                    st.image("https://via.placeholder.com/300x300?text=No+Image", use_container_width=True)
                
                # Product details
                st.markdown(f"**{product['Name'][:60]}{'...' if len(str(product['Name'])) > 60 else ''}**")
                st.caption(f"🏷️ {product['Brand']}")
                
                # Rating display
                rating = float(product['Rating'])
                stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
                st.markdown(f"{stars} **{rating:.1f}**/5")
                
                st.markdown("---")

# ---------------- MAIN CONTENT ----------------
st.title("🛒 MyCart Product Recommendations")
st.markdown("Discover products tailored to your preferences")

# Search section
st.markdown("### 🔍 Search for Products")

col1, col2 = st.columns([4, 1])

with col1:
    # Check if there's a selected search from history
    default_value = st.session_state.get('selected_search', '')
    product_name = st.text_input(
        "Product Name",
        value=default_value,
        placeholder="e.g., OPI Nail Polish, Samsung Galaxy, Nike Shoes...",
        label_visibility="collapsed"
    )
    # Clear the selected search after using it
    if 'selected_search' in st.session_state:
        del st.session_state.selected_search

with col2:
    submit = st.button("🔍 Search", type="primary", use_container_width=True)

st.markdown("---")

# ---------------- DISPLAY RECOMMENDATIONS ----------------

# Always show highly rated products
st.markdown('<div class="section-header">⭐ Highly Rated Products</div>', unsafe_allow_html=True)
st.markdown("*Top picks based on customer ratings*")
st.markdown("")

with st.spinner('Loading top rated products...'):
    rating_based_df = get_rating_based_recommendations(top_n=8)
    display_product_grid(rating_based_df, columns=4)

# Show search-based recommendations if submitted
if submit and product_name.strip():
    add_to_search_history(product_name)
    
    # Content Based Recommendations
    st.markdown('<div class="section-header">🎯 Similar Products</div>', unsafe_allow_html=True)
    st.markdown(f"*Products similar to '{product_name}'*")
    st.markdown("")
    
    with st.spinner('Finding similar products...'):
        content_based_df = get_content_based_recommendations(product_name, top_n=8)
        display_product_grid(content_based_df, columns=4)
    
    # Collaborative Recommendations (only for logged-in users)
    if user_id != 0:
        st.markdown('<div class="section-header">👥 Recommended for You</div>', unsafe_allow_html=True)
        st.markdown(f"*Based on users with similar preferences (User ID: {user_id})*")
        st.markdown("")
        
        with st.spinner('Personalizing recommendations...'):
            collab_based_df = get_collaborative_recommendations(user_id, top_n=8)
            display_product_grid(collab_based_df, columns=4)
    else:
        st.info("💡 **Tip:** Enter your User ID to get personalized recommendations!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; padding: 2rem;'>"
    "Built with ❤️ using Streamlit | Powered by Machine Learning"
    "</div>",
    unsafe_allow_html=True
)