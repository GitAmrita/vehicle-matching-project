import uuid
from typing import List, Dict, Any
from es_module.elasticsearch_client import client, INDEX_NAME, test_connection, check_index_exists
from database.db import fetch_canonical_models
from data.noisy_data.noise import MAKE_ABBR_MAP
from tqdm import tqdm
from elasticsearch.helpers import bulk


def create_index(index_name: str = INDEX_NAME, recreate: bool = False):
    """
    Create Elasticsearch index with optimized mappings for vehicle search.
    
    Features:
    - Custom analyzers for fuzzy matching and typo tolerance
    - Edge n-grams for autocomplete
    - Synonym support for make abbreviations
    - Proper field types for filtering (year, make, model)
    
    Args:
        index_name: Name of the index to create
        recreate: If True, delete existing index and create new one
    """
    # Test connection first
    test_connection()
    
    # Delete index if it exists and recreate is True
    if recreate and check_index_exists(index_name):
        print(f"🗑️  Deleting existing index: {index_name}")
        client.indices.delete(index=index_name)
    
    # Check if index already exists
    if check_index_exists(index_name):
        print(f"ℹ️  Index '{index_name}' already exists. Use recreate=True to overwrite.")
        return
    
    # Define index settings with custom analyzers
    index_settings = {
        "settings": {
            "number_of_shards": 1,  # Single shard for small dataset
            "number_of_replicas": 0,  # No replicas for local development
            "analysis": {
                "analyzer": {
                    "vehicle_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding",  # Handle accents
                            "synonym_filter",  # For make abbreviations (must come before n-gram)
                            "edge_ngram_filter"  # For partial matching (after synonyms)
                        ]
                    },
                    "fuzzy_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding"
                        ]
                    }
                },
                "filter": {
                    "edge_ngram_filter": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 15
                    },
                    "synonym_filter": {
                        "type": "synonym",
                        "synonyms": _build_synonym_list()
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "make": {
                    "type": "text",
                    "analyzer": "vehicle_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword"  # For exact matching/filtering
                        }
                    }
                },
                "model": {
                    "type": "text",
                    "analyzer": "vehicle_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword"  # For exact matching/filtering
                        }
                    }
                },
                "year": {
                    "type": "integer"  # For range queries
                },
                "normalized_text": {
                    "type": "text",
                    "analyzer": "vehicle_analyzer",
                    "fields": {
                        "fuzzy": {
                            "type": "text",
                            "analyzer": "fuzzy_analyzer"
                        }
                    }
                },
                "make_aliases": {
                    "type": "text",
                    "analyzer": "vehicle_analyzer"
                },
                "make_id": {
                    "type": "keyword"
                },
                "model_id": {
                    "type": "keyword"
                }
            }
        }
    }
    
    # Create the index
    # Elasticsearch 8.x accepts settings and mappings as separate parameters
    try:
        client.indices.create(
            index=index_name,
            settings=index_settings['settings'],
            mappings=index_settings['mappings']
        )
        print(f"✅ Created index: {index_name}")
    except Exception as e:
        # Fallback: try with body parameter (older API)
        try:
            client.indices.create(index=index_name, body=index_settings)
            print(f"✅ Created index: {index_name} (using body parameter)")
        except Exception as e2:
            print(f"❌ Error creating index: {e2}")
            raise


def _build_synonym_list() -> List[str]:
    """
    Build synonym list from MAKE_ABBR_MAP for Elasticsearch synonym filter.
    Returns list of synonym pairs in Elasticsearch format: "make,abbreviation"
    """
    synonyms = []
    for make_name, abbr in MAKE_ABBR_MAP.items():
        if abbr and abbr != make_name:
            # Format: "full_name,abbreviation" (both ways)
            synonyms.append(f"{make_name.lower()},{str(abbr).lower()}")
            synonyms.append(f"{str(abbr).lower()},{make_name.lower()}")
    return synonyms


def build_index(limit: int = 1000, offset: int = 0, index_name: str = INDEX_NAME, batch_size: int = 100):
    """
    Build and populate Elasticsearch index from SQLite database.
    
    Args:
        limit: Maximum number of records to fetch
        offset: Starting offset for fetching records
        index_name: Name of the Elasticsearch index
        batch_size: Number of documents to index per batch
        
    Returns:
        Number of documents indexed
    """
    # Ensure index exists
    if not check_index_exists(index_name):
        print(f"📝 Creating index: {index_name}")
        create_index(index_name, recreate=False)
    
    # Fetch canonical data from SQLite
    rows = fetch_canonical_models(limit=limit, offset=offset)
    print(f"📊 Fetched {len(rows)} canonical models from offset {offset}")
    
    if not rows:
        print("⚠️  No data to index")
        return 0
    
    # Prepare documents for indexing
    documents = []
    for (make_name, model_name, year) in rows:
        # Normalize text (same as Qdrant)
        text = f"{year} {make_name} {model_name}".strip().lower().replace("  ", " ") if model_name else f"{year} {make_name}".lower()
        
        # Get make abbreviation/aliases
        abbr = MAKE_ABBR_MAP.get(make_name)
        alias_set = {make_name.lower()}
        if abbr:
            alias_set.add(str(abbr).lower())
        
        # Create document
        doc = {
            "make": make_name,
            "model": model_name,
            "year": int(year),
            "normalized_text": text,
            "make_aliases": list(alias_set),
            # Store IDs if available (for future reference)
            "make_id": None,  # Could be fetched from DB if needed
            "model_id": None,  # Could be fetched from DB if needed
        }
        documents.append(doc)
    
    # Index documents in batches
    indexed_count = 0
    print(f"📤 Indexing {len(documents)} documents in batches of {batch_size}...")
    
    for i in tqdm(range(0, len(documents), batch_size), desc="Indexing"):
        batch = documents[i:i + batch_size]
        
        # Prepare bulk operations
        actions = []
        for doc in batch:
            actions.append({
                "_index": index_name,
                "_id": uuid.uuid4().hex,  # Generate unique ID
                "_source": doc
            })
        
        # Bulk index
        try:
            success, failed = bulk(client, actions, raise_on_error=False)
            indexed_count += success
            
            if failed:
                print(f"⚠️  {len(failed)} documents failed to index in this batch")
        except Exception as e:
            print(f"❌ Error indexing batch {i//batch_size + 1}: {e}")
            raise
    
    # Refresh index to make documents searchable immediately
    client.indices.refresh(index=index_name)
    
    print(f"✅ Successfully indexed {indexed_count} documents!")
    return indexed_count


def get_index_stats(index_name: str = INDEX_NAME):
    """
    Get statistics about the index.
    
    Args:
        index_name: Name of the index
        
    Returns:
        Dictionary with index statistics
    """
    try:
        if not check_index_exists(index_name):
            return None
        
        stats = client.indices.stats(index=index_name)
        count_result = client.count(index=index_name)
        
        return {
            "document_count": count_result["count"],
            "size_bytes": stats["indices"][index_name]["total"]["store"]["size_in_bytes"],
            "size_mb": round(stats["indices"][index_name]["total"]["store"]["size_in_bytes"] / 1024 / 1024, 2)
        }
    except Exception as e:
        print(f"❌ Error getting index stats: {e}")
        return None

