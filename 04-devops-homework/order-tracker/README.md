# Order Tracker

A small order tracking app for the AI Dev Tools Zoomcamp observability homework. It includes a web page, API, tests, and a Docker Compose setup. You add telemetry, alerts, and an incident responder in Homework 4.

The main user flow is creating an order and checking its status. Three sample orders are created on first startup.

## Run it

You need Docker with Compose. To run the tests, you also need Python 3.11+ and `uv`.

```bash
docker compose up --build -d --wait
```

Open <http://127.0.0.1:8000>. The API is at `/api/orders`, and the health check is at `/healthz`. Data is stored in a Docker volume and survives container recreation.

If port 8000 is occupied, set `ORDER_TRACKER_PORT`, for example:

```bash
ORDER_TRACKER_PORT=18080 docker compose up --build -d --wait
```

Run tests with `uv run --frozen pytest -q`. Stop the app with `docker compose down`. Add `-v` only if you also want to delete the order data.

Order lookups emit OpenTelemetry request-count metrics, traces, and structured logs. In Compose, the app sends them over OTLP to the Collector, which routes metrics to Prometheus, logs to Loki, and traces to Tempo. The metric includes `http.route` and `http.response.status_code`. Console output is also retained for inspection:

```bash
docker compose logs -f app
```

Open Grafana at <http://127.0.0.1:3000> (user `admin`, password `admin` unless `GRAFANA_ADMIN_PASSWORD` is set). The provisioned **Order Tracker - HTTP** dashboard shows request counts by route/status and failed lookups (4xx/5xx). Prometheus is also available at <http://127.0.0.1:9090>.

Grafana provisions the **Order Tracker 5xx responses** alert and routes it to the `incident-responder` webhook contact point through a child notification policy. It checks for 5xx order lookups over five minutes, links to the HTTP dashboard, and treats no matching responses as zero (`Normal`). Check its current state under **Alerting → Alert rules** in Grafana. The alert, contact point, and notification policy are configured under `grafana/provisioning/alerting/`.

## Incident response

The `incident-response` service listens on <http://127.0.0.1:8001/alerts> for Grafana webhook payloads. Firing alerts for the order lookup endpoint are saved as JSON under the `incident-records` volume, enriched with matching Loki logs and Tempo traces, and handed to GitHub Copilot CLI in headless mode. Repeated webhook deliveries with the same fingerprint are deduplicated.

To enable Copilot, copy `.env.example` to `.env` and set `GH_TOKEN` to a fine-grained GitHub token with the **Copilot Requests** permission. Keep `.env` private; it is ignored by Git. Then rebuild with `docker compose up --build -d --wait`. The container runs Copilot with automatic tool approval to meet the unattended requirement, but has no Docker socket and only mounts `app/` and `tests/` as writable workspace folders. Review those changes after an incident. An optional `INCIDENT_WEBHOOK_TOKEN` requires Grafana to send `Authorization: Bearer <token>`; leave it unset until adding the matching header to the Grafana contact point.

The incident API accepts Grafana's standard `alerts` array at `POST /alerts`, and exposes saved records at `GET /incidents/{incident_id}`. Use `GET /healthz` to check whether Copilot is installed and authenticated.

For a non-mutating responder smoke test, send an alert with `labels.test: "true"` and no endpoint. The receiver stores it without querying telemetry and asks Copilot only to confirm receipt. The returned incident ID can be used with `GET /incidents/{incident_id}`; the CLI reply is in `assistant.stdout`.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Web page |
| GET | `/healthz` | Database health check |
| GET | `/api/orders` | List orders |
| POST | `/api/orders` | Create an order |
| GET | `/api/orders/{id}` | Check an order |
| PATCH | `/api/orders/{id}` | Change an order status |

The app uses SQLite to keep setup small. Run one app container at a time. The course exercise is about detecting and handling an incident, not scaling the database.
