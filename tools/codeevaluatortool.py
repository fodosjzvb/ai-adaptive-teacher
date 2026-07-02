import importlib.util
import sys
import traceback


class CodeEvaluatorTool:

    def run(self, file_path, function_name, tests):
        try:
            # Charger dynamiquement le fichier Python
            spec = importlib.util.spec_from_file_location("user_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            func = getattr(module, function_name, None)

            if func is None:
                return {
                    "passed": False,
                    "score": 0,
                    "error": f"Function {function_name} not found"
                }

            passed = 0
            failed_tests = []

            for test in tests:
                inputs = test[0]
                expected = test[1]

                try:
                    result = func(*inputs)

                    if result == expected:
                        passed += 1
                    else:
                        failed_tests.append({
                            "inputs": inputs,
                            "expected": expected,
                            "got": result
                        })

                except Exception as e:
                    failed_tests.append({
                        "inputs": inputs,
                        "error": str(e)
                    })

            total = len(tests)
            score = int((passed / total) * 100)

            return {
                "passed": score == 100,
                "score": score,
                "passed_tests": passed,
                "total_tests": total,
                "failed_tests": failed_tests
            }

        except Exception:
            return {
                "passed": False,
                "score": 0,
                "error": traceback.format_exc()
            }