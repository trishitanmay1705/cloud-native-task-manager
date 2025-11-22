import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from .database import init_db, db
from .models import Task

# Prometheus metrics
REQUEST_COUNT = Counter(
    "taskmanager_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)

REQUEST_LATENCY = Histogram(
    "taskmanager_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"],
)


def create_app():
    app = Flask(__name__)
    CORS(app)
    init_db(app)

    @app.before_request
    def before_request():
        request.start_time = datetime.utcnow()

    @app.after_request
    def after_request(response):
        try:
            latency = (datetime.utcnow() - request.start_time).total_seconds()
            endpoint = request.path
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                http_status=response.status_code,
            ).inc()
        except Exception:
            # don't break the app for metrics issues
            pass
        return response

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/metrics", methods=["GET"])
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    # ---- TASKS CRUD ----

    @app.route("/api/tasks", methods=["GET"])
    def list_tasks():
        status = request.args.get("status")
        query = Task.query
        if status:
            query = query.filter_by(status=status)
        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tasks]), 200

    @app.route("/api/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200

    @app.route("/api/tasks", methods=["POST"])
    def create_task():
        data = request.get_json() or {}
        title = data.get("title")
        if not title:
            return jsonify({"error": "title is required"}), 400

        description = data.get("description")
        status = data.get("status", "pending")
        due_date_str = data.get("due_date")
        due_date = None

        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                return jsonify({"error": "Invalid due_date format, use ISO 8601"}), 400

        task = Task(
            title=title,
            description=description,
            status=status,
            due_date=due_date,
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    @app.route("/api/tasks/<int:task_id>", methods=["PUT", "PATCH"])
    def update_task(task_id):
        task = Task.query.get_or_404(task_id)
        data = request.get_json() or {}

        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "status" in data:
            task.status = data["status"]
        if "due_date" in data:
            due_date_str = data.get("due_date")
            if due_date_str:
                try:
                    task.due_date = datetime.fromisoformat(due_date_str)
                except ValueError:
                    return jsonify({"error": "Invalid due_date format"}), 400
            else:
                task.due_date = None

        db.session.commit()
        return jsonify(task.to_dict()), 200

    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "deleted"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
