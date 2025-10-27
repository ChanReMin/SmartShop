from app import create_app
from app.tasks.scheduler import start_scheduler

app = create_app()
# start_scheduler(app, timeout_seconds=60, interval_seconds=60)

if __name__ == "__main__":
    app.run(debug=True)
