from excel_reader import load_requests
from scoring import calculate_priority
from decision import make_decision
from report_generator import generate_report


def process_requests():
    requests = load_requests()
    processed_requests = []

    for request in requests:
        priority_data = calculate_priority(request)
        request.update(priority_data)

        decision_data = make_decision(request)
        request.update(decision_data)

        processed_requests.append(request)

    return processed_requests


if __name__ == "__main__":
    results = process_requests()

    print("\nBPO PRIORITY DECISION PLATFORM")
    print("=" * 45)
    print(f"Total requests analyzed: {len(results)}")

    for request in results:
        print(
            f"{request['request_id']} | "
            f"{request['priority']} | "
            f"{request['decision']}"
        )

    report_path = generate_report(results)
    print("\nReport generated successfully:")
    print(report_path)