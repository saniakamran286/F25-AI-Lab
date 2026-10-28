def check_result(marks, attendance, disciplinary_issue):
    # Condition 1: Marks should be 70 or above
    if marks < 70:
        return "FAIL", "Marks are below 70."

    # Condition 2: Attendance should be 75% or above
    elif attendance < 75:
        return "FAIL", "Attendance is below 75%."

    # Condition 3: Student should not have any disciplinary issue
    elif disciplinary_issue:
        return "FAIL", "Student has a disciplinary issue."

    else:
        return "PASS", "All conditions satisfied."


# Four main test scenarios

test_cases = [
    {
        "name": "Case 1",
        "marks": 92,
        "attendance": 88,
        "disciplinary_issue": False
    },
    {
        "name": "Case 2",
        "marks": 58,
        "attendance": 94,
        "disciplinary_issue": False
    },
    {
        "name": "Case 3",
        "marks": 78,
        "attendance": 62,
        "disciplinary_issue": False
    },
    {
        "name": "Case 4",
        "marks": 81,
        "attendance": 86,
        "disciplinary_issue": True
    }
]

for case in test_cases:
    result, reason = check_result(
        case["marks"],
        case["attendance"],
        case["disciplinary_issue"]
    )

    print(case["name"])
    print("Input:", case)
    print("Expected Result:",
          "PASS" if case["name"] == "Case 1" else "FAIL")
    print("Actual Result:", result)
    print("Reason:", reason)
    print("-" * 50)
