import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError

# --- Config ---
# Local development (Docker Compose)
ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "http://localhost:9200")
ELASTICSEARCH_USER = os.environ.get("ELASTICSEARCH_USER", None)
ELASTICSEARCH_PASSWORD = os.environ.get("ELASTICSEARCH_PASSWORD", None)

# Elastic Cloud support (optional)
ELASTICSEARCH_CLOUD_ID = os.environ.get("ELASTICSEARCH_CLOUD_ID", None)
ELASTICSEARCH_API_KEY = os.environ.get("ELASTICSEARCH_API_KEY", None)

# Index name
INDEX_NAME = os.environ.get("ELASTICSEARCH_INDEX_NAME", "vehicles")

# --- Connect to Elasticsearch ---
def create_client():
    """
    Create and return an Elasticsearch client.
    Supports both local Docker setup and Elastic Cloud.
    """
    # Common connection parameters
    # Set API compatibility to version 8 to match Elasticsearch 8.11.0 server
    # Use headers parameter to force API version 8 compatibility
    common_params = {
        'request_timeout': 30,
        'max_retries': 3,
        'retry_on_timeout': True,
        # Force API version 8 compatibility (required for Elasticsearch 8.x servers)
        'headers': {
            'Accept': 'application/vnd.elasticsearch+json; compatible-with=8',
            'Content-Type': 'application/vnd.elasticsearch+json; compatible-with=8'
        }
    }
    
    # Elastic Cloud connection (priority)
    if ELASTICSEARCH_CLOUD_ID and ELASTICSEARCH_API_KEY:
        return Elasticsearch(
            cloud_id=ELASTICSEARCH_CLOUD_ID,
            api_key=ELASTICSEARCH_API_KEY,
            **common_params
        )
    # Local Docker connection with authentication (if provided)
    elif ELASTICSEARCH_USER and ELASTICSEARCH_PASSWORD:
        return Elasticsearch(
            hosts=[ELASTICSEARCH_HOST],
            basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
            **common_params
        )
    # Local Docker connection without authentication (default for development)
    else:
        return Elasticsearch(
            hosts=[ELASTICSEARCH_HOST],
            **common_params
        )

# Create the client instance
client = create_client()


def test_connection():
    """
    Test Elasticsearch connection and return cluster info.
    Raises exception if connection fails.
    """
    try:
        info = client.info()
        cluster_name = info.get('cluster_name', 'unknown')
        version = info.get('version', {}).get('number', 'unknown')
        print(f"✅ Connected to Elasticsearch cluster: {cluster_name} (v{version})")
        return True
    except ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Make sure Elasticsearch is running at {ELASTICSEARCH_HOST}")
        print(f"   Try: docker-compose up -d")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


def check_index_exists(index_name: str = INDEX_NAME) -> bool:
    """
    Check if an index exists.
    
    Args:
        index_name: Name of the index to check
        
    Returns:
        True if index exists, False otherwise
    """
    try:
        return client.indices.exists(index=index_name)
    except Exception as e:
        print(f"❌ Error checking index existence: {e}")
        return False


def get_index_info(index_name: str = INDEX_NAME):
    """
    Get information about an index.
    
    Args:
        index_name: Name of the index
        
    Returns:
        Dictionary with index information
    """
    try:
        if not check_index_exists(index_name):
            return None
        
        stats = client.indices.stats(index=index_name)
        mapping = client.indices.get_mapping(index=index_name)
        
        return {
            'exists': True,
            'document_count': stats['indices'][index_name]['total']['docs']['count'],
            'size': stats['indices'][index_name]['total']['store']['size_in_bytes'],
            'mapping': mapping[index_name]['mappings']
        }
    except Exception as e:
        print(f"❌ Error getting index info: {e}")
        return None


# Export for use in other modules
__all__ = [
    'client',
    'INDEX_NAME',
    'ELASTICSEARCH_HOST',
    'test_connection',
    'check_index_exists',
    'get_index_info',
]

