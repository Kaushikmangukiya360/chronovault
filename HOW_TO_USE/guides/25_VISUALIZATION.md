# Visualization Guide

## Purpose
This guide explains how to add visualization workflows for ChronoVault operations so teams can monitor usage, performance, and security trends.

## Why visualization matters
Visualization helps with:
- Audit event trend monitoring
- Query and search performance tracking
- Shard/storage growth planning
- Tenant activity analysis and anomaly detection

## Recommended visualization data domains

### 1) Audit Trends
Suggested metrics:
- Events per minute/hour/day by event type
- Success/denied/error ratios
- Top collections by read/write volume

### 2) Query and Search Performance
Suggested metrics:
- Query execution count by operator type
- Search usage over time
- Aggregation and join frequency

### 3) Storage and Shard Utilization
Suggested metrics:
- Total records per collection
- Records per shard distribution
- Growth trend by tenant and collection

### 4) Tenant Activity
Suggested metrics:
- Active token usage over time
- Access patterns by role (admin/editor/viewer)
- IP allowlist rejection trend

## Implementation pattern

1. Build an internal metrics exporter layer in ChronoVault.
2. Aggregate data from encrypted audit and metadata payloads.
3. Expose chart-ready JSON through controlled APIs.
4. Render with your preferred visualization stack.

## Example chart-ready payload shape

```json
{
  "window": "24h",
  "audit": {
    "events_by_hour": [
      {"hour": "2026-03-25T00:00:00Z", "read": 120, "write": 30, "error": 2}
    ]
  },
  "storage": {
    "collections": [
      {"name": "users", "records": 2100, "shards": 1},
      {"name": "orders", "records": 18450, "shards": 2}
    ]
  }
}
```

## Security notes
- Do not expose token secrets, key material, or decrypted PII in visualization payloads.
- Enforce role checks before serving visualization metrics.
- Prefer aggregate metrics over raw record-level data.

## Integration options
- FastAPI dashboard endpoint that returns chart-ready JSON
- Static reports generated from CLI exports
- External observability systems (via sanitized metrics export)

## Next implementation tasks
- Add visualization exporter module in core package.
- Add CLI commands for visualization report generation.
- Add tests for payload correctness and redaction safety.
