from pinecone import Pinecone
import os

pc = Pinecone(api_key="pcsk_224y16_BG5nWLCeN5e4ciEcbw2GNzMowk7s8U5PpGRSmg9KA2UgQnuSHyZhK9BtMk88qvu")

# List your indexes first to see the name
indexes = pc.list_indexes()
print("Your indexes:", indexes)

# Then delete — replace with your actual index name from the output above
# pc.delete_index("your-actual-index-name")