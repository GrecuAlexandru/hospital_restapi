import uvicorn
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Hospital REST API server")
    parser.add_argument(
        "--with-fixtures",
        action="store_true",
        help="Initialize database with test fixtures",
    )

    args = parser.parse_args()

    if args.with_fixtures:
        sys.argv.append("--with-fixtures")
        print("Starting with fixtures initialization...")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
