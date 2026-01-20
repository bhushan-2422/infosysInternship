import pandas as pd
import sklearn
from sklearn.metrics.pairwise import cosine_similarity

def collaborative_filtering_recommendations(data, target_user_id, top_n=10):
    user_item_matrix = data.pivot_table(index='ID', columns='ProdID', values='Rating', aggfunc='mean').fillna(0)
    user_similarity = cosine_similarity(user_item_matrix)
    target_user_index = user_item_matrix.index.get_loc(target_user_id)
    user_similarities = user_similarity[target_user_index]
    similar_users_indices = user_similarities.argsort()[::-1][1:]
    
    recommended_items = []
    seen_items = set()  # Track unique items

    for user_index in similar_users_indices:
        if len(recommended_items) >= top_n:  # Stop when we have enough recommendations
            break
            
        rated_by_similar_user = user_item_matrix.iloc[user_index]
        not_rated_by_target_user = (rated_by_similar_user != 0) & (user_item_matrix.iloc[target_user_index] == 0)
        
        # Get items rated by this similar user
        candidate_items = user_item_matrix.columns[not_rated_by_target_user].tolist()
        
        # Add unique items until we reach top_n
        for item in candidate_items:
            if item not in seen_items:
                recommended_items.append(item)
                seen_items.add(item)
                if len(recommended_items) >= top_n:
                    break
    
    # Get details for recommended items and remove duplicates
    recommended_items_details = data[data['ProdID'].isin(recommended_items)][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']].drop_duplicates(subset=['Name'])
    
    # Limit to exactly top_n items
    return recommended_items_details.head(top_n)

# Example usage
if __name__ == "__main__":
    import pandas as pd
    from preprocess_data import process_data

    raw_data = pd.read_csv("clean_data.csv")
    data = process_data(raw_data)

    target_user_id = 4
    print(collaborative_filtering_recommendations(data, target_user_id, top_n=10))