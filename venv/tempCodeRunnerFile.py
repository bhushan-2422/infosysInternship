# To get content based recommended items
# item_name = 'OPI Infinite Shine, Nail Lacquer Nail Polish, Bubble Bath'
# content_based_recom = content_based_recommendation(data, item_name, top_n = 8)
# print("\nContent-based recommendations:")
# content_based_recom

# # To get Collaborative based recommended items
# target_user_id = 4
# collaborative_filtering_rec = collaborative_filtering_recommendations(data, target_user_id, 
#                                                                       top_n = 5)
# print("\nCollaborative filtering recommendations:")
# collaborative_filtering_rec

# # Hybrid recommendation
# hybrid_rec = hybrid_recommendation_filtering(
#     data,
#     item_name=item_name,
#     target_user_id=target_user_id,
#     top_n=5
# )

# # Fallback if hybrid is empty
# if hybrid_rec.empty:
#     print("\nHybrid was empty, showing top-rated items instead")
#     hybrid_rec = get_top_rated_items(data, top_n=5)

# print("\nHybrid recommendations:")
# hybrid_rec