from UnanimityCalculator import Calculator

# calculator
calc = Calculator(
    {
        "a": [],
        "c": [],
        "d": [],
        "e": []
    }
)

# show results
print("--- unanimity and ranking analysis ---")
calc.showResults()
print("\n--- lowest sum ---")
calc.showRankingAnalysis()
