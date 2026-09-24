from src.evaluator import valid_plan_rate


def test_valid_plan_rate():
    results = [
        {"valid": True},
        {"valid": False},
        {"valid": True},
        {"valid": True},
    ]

    score = valid_plan_rate(results)

    assert score == 0.75


if __name__ == "__main__":
    test_valid_plan_rate()

    print("Setup test passed.")