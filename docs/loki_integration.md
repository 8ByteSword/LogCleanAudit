# This package can be integrated with grafana using loki. For now just for locally deployed.

## Deploy loki

```bash
docker run -p 3100:3100 \
    -v /path/to/loki.yaml:/etc/loki/local-config.yaml \
    grafana/loki:latest \
    -config.file=/etc/loki/local-config.yaml
```
### yaml example

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 127.0.0.1
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 1h       # Any value greater than 0
  chunk_retain_period: 30s    # Any value greater than 0
  max_transfer_retries: 0     # 0 or greater

```

## Install and run grafana service

```bash
    sudo apt-get install -y adduser libfontconfig1
    wget https://dl.grafana.com/enterprise/release/grafana-enterprise_9.4.7_amd64.deb
    sudo dpkg -i grafana-enterprise_9.4.7_amd64.deb
    sh grafana-server
    sudo service grafana-server start #For some reason it worked for me after 2 tryes
```