# Elasticsearch Setup Guide

## Quick Start

### 1. Start Elasticsearch + Kibana
```bash
docker-compose up -d
```

### 2. Check Status
```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f elasticsearch
docker-compose logs -f kibana
```

### 3. Verify Elasticsearch is Running
```bash
# Should return cluster information
curl http://localhost:9200

# Check cluster health
curl http://localhost:9200/_cluster/health?pretty
```

### 4. Access Kibana (Optional but Recommended)
Open in browser: http://localhost:5601

Kibana provides:
- **Dev Tools**: Test Elasticsearch queries interactively
- **Index Management**: View and manage indices
- **Search Profiler**: Debug slow queries
- **Visualizations**: Create dashboards (for analytics)

## Common Commands

### Stop Services
```bash
docker-compose stop
```

### Restart Services
```bash
docker-compose restart
```

### Stop and Remove Containers (keeps data)
```bash
docker-compose down
```

### Stop and Remove Everything (including data)
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Just Elasticsearch
docker-compose logs -f elasticsearch
```

### Check Resource Usage
```bash
docker stats vehicle-elasticsearch vehicle-kibana
```

## Troubleshooting

### Elasticsearch won't start / Out of Memory
If you see memory errors, adjust the heap size in `docker-compose.yml`:

```yaml
- "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # Lower for less powerful machines
```

### Port Already in Use
If port 9200 or 5601 is already taken, change in `docker-compose.yml`:

```yaml
ports:
  - "9201:9200"  # Use 9201 on host instead
```

### Cannot Connect from Python
Make sure containers are healthy:
```bash
docker-compose ps
# STATUS should show "healthy" for elasticsearch
```

### Reset Everything
If things get weird, nuclear option:
```bash
docker-compose down -v  # Remove containers and volumes
docker-compose up -d    # Start fresh
```

## Data Persistence

Data is stored in a Docker volume named `elasticsearch-data`. This means:
- ✅ Data persists between `docker-compose down` and `up`
- ✅ Indices survive container restarts
- ❌ Data is lost if you run `docker-compose down -v`

To backup data:
```bash
# Create snapshot (inside container)
docker exec vehicle-elasticsearch \
  curl -X PUT "localhost:9200/_snapshot/my_backup"
```

## Production Migration

When ready for Elastic Cloud:
1. Export data using Elasticsearch snapshots
2. Update `database/elasticsearch_client.py` with cloud credentials
3. Import data to cloud cluster
4. Update `docker-compose.yml` to remove or comment out ES service

## Useful Kibana Dev Tools Queries

```json
# View all indices
GET /_cat/indices?v

# Check specific index mapping
GET /vehicles/_mapping

# Search vehicles
GET /vehicles/_search
{
  "query": {
    "match": {
      "make": "Toyota"
    }
  }
}

# Delete an index (careful!)
DELETE /vehicles
```

## Next Steps

1. ✅ Start services: `docker-compose up -d`
2. ✅ Verify: `curl http://localhost:9200`
3. ✅ Open Kibana: http://localhost:5601
4. 🚀 Run Python indexing scripts (coming next!)

