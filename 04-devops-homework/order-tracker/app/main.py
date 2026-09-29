import os
import sqlite3
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from opentelemetry._logs import LogRecord, SeverityNumber
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogRecordExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.trace import Status, StatusCode
from pydantic import BaseModel, Field


DB_PATH = Path(os.getenv("ORDER_DB_PATH", "data/orders.db"))
STATUSES = {"received", "preparing", "shipped", "delivered"}
ORDER_ROUTE = "/api/orders/{order_id}"

resource = Resource.create({"service.name": "order-tracker"})
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter(out=sys.__stdout__))
)
if otlp_endpoint:
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    )
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("order-tracker")

metric_readers = [
    PeriodicExportingMetricReader(
        ConsoleMetricExporter(out=sys.__stdout__), export_interval_millis=5000
    )
]
if otlp_endpoint:
    metric_readers.append(
        PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True),
            export_interval_millis=5000,
        )
    )
meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
metrics.set_meter_provider(meter_provider)
order_lookup_requests = metrics.get_meter("order-tracker").create_counter(
    "http.server.request.count",
    unit="{request}",
    description="Number of order lookup requests",
)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    SimpleLogRecordProcessor(ConsoleLogRecordExporter(out=sys.__stdout__))
)
if otlp_endpoint:
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=otlp_endpoint, insecure=True))
    )
otel_logger = logger_provider.get_logger("order-tracker")


def record_order_lookup(order_id: str, status_code: int, outcome: str) -> None:
    metric_attributes = {
        "http.route": ORDER_ROUTE,
        "http.response.status_code": status_code,
    }
    log_attributes = {
        **metric_attributes,
        "order.id": order_id,
        "order.lookup.outcome": outcome,
    }
    order_lookup_requests.add(1, metric_attributes)
    severity = SeverityNumber.ERROR if status_code >= 500 else SeverityNumber.INFO
    otel_logger.emit(
        LogRecord(
            body="Order lookup completed",
            severity_text="ERROR" if status_code >= 500 else "INFO",
            severity_number=severity,
            attributes=log_attributes,
        )
    )


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer TEXT NOT NULL,
                item TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        if db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0:
            now = datetime.now(timezone.utc)
            previous_month_end = now.replace(day=1) - timedelta(days=1)
            for order in (
                ("standard-1001", "Avery", "Notebook", "standard", "received", now),
                ("express-1002", "Sam", "Headphones", "express", "preparing", previous_month_end),
                ("standard-1003", "Riley", "Water bottle", "standard", "shipped", now),
            ):
                db.execute(
                    "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
                    (*order[:5], order[5].isoformat()),
                )


def as_dict(row):
    return dict(row) if row else None


def order_detail(row):
    order = as_dict(row)
    if order["priority"] == "express":
        placed_at = datetime.fromisoformat(order["created_at"])
        estimated_at = placed_at + timedelta(days=2)
        order["estimated_delivery"] = estimated_at.date().isoformat()
    return order


class NewOrder(BaseModel):
    customer: str = Field(min_length=1, max_length=80)
    item: str = Field(min_length=1, max_length=120)
    priority: str = "standard"


class StatusUpdate(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Order Tracker", lifespan=lifespan)


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")


@app.get("/healthz")
def health():
    with connect() as db:
        db.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/api/orders")
def list_orders():
    with connect() as db:
        rows = db.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    return [as_dict(row) for row in rows]


def load_order(order_id: str):
    with connect() as db:
        row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Order not found")
    return order_detail(row)


@app.get(ORDER_ROUTE)
def get_order(order_id: str):
    with tracer.start_as_current_span(
        "order.lookup", record_exception=False, set_status_on_exception=False
    ) as span:
        span.set_attribute("http.route", ORDER_ROUTE)
        span.set_attribute("order.id", order_id)
        try:
            order = load_order(order_id)
        except HTTPException as error:
            span.set_attribute("http.response.status_code", error.status_code)
            if error.status_code >= 500:
                span.set_status(Status(StatusCode.ERROR, str(error.detail)))
            record_order_lookup(order_id, error.status_code, "not_found")
            raise
        except Exception as error:
            span.set_attribute("http.response.status_code", 500)
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            record_order_lookup(order_id, 500, "error")
            raise

        span.set_attribute("http.response.status_code", 200)
        record_order_lookup(order_id, 200, "found")
        return order


@app.post("/api/orders", status_code=201)
def create_order(order: NewOrder):
    if order.priority not in {"standard", "express"}:
        raise HTTPException(422, "Priority must be standard or express")
    order_id = str(uuid4())
    with connect() as db:
        db.execute(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, order.customer, order.item, order.priority, "received",
             datetime.now(timezone.utc).isoformat()),
        )
    return load_order(order_id)


@app.patch("/api/orders/{order_id}")
def update_status(order_id: str, update: StatusUpdate):
    if update.status not in STATUSES:
        raise HTTPException(422, "Invalid status")
    with connect() as db:
        cursor = db.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (update.status, order_id),
        )
    if cursor.rowcount == 0:
        raise HTTPException(404, "Order not found")
    return load_order(order_id)
