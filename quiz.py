import json
import random
import sys


def parse_args() -> tuple[str, int]:
    if len(sys.argv) < 2:
        raise ValueError
    examples_filename = sys.argv[1]
    assert examples_filename.endswith(".jsonl")
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    return examples_filename, count


def score_p(p: float) -> float:
    return 1 - (1 - p) ** 2


def attempt_problem(problem) -> tuple[float, float]:
    prompt, policy = problem["prompts"]["ansi"], problem["policy"]
    print(prompt)
    guess = input().strip().upper()
    if guess not in policy:
        print("Invalid move: -1 point.")
        return -1
    score = score_p(policy[guess])
    best_move, best_p = max(policy.items(), key=lambda item: item[1])
    best_score = score_p(best_p)
    if best_score == score:
        print(f"Perfect! {score:.3f} points.")
    else:
        print(
            f"Best move was {best_move}. Score: {score:.3f} out of possible {best_score:.3f}"
        )
    return best_score, best_score


def main():
    try:
        examples_filename, count = parse_args()
    except (AssertionError, ValueError):
        print(
            "Usage: python quiz.py <examples_filename.jsonl> [number of examples to try]"
        )
    with open(examples_filename, "r") as f:
        examples = [json.loads(line) for line in f]
        print(f"Loaded {len(examples)} examples from {examples_filename}...")
        random.shuffle(examples)
        if len(examples) < count:
            print(
                f"{count} examples were requested, but only {len(examples)} are available."
            )
            count = len(examples)
        print(f"Beginning quiz on {count} problems...")
        score = 0
        max_score = 0
        for example in examples[:count]:
            p_score, max_p_score = attempt_problem(example)
            score += p_score
            max_score += max_p_score
        print()
        print(
            f"Problem set complete! Total score: {score:.3f} out of a possible {max_score:.3f} points."
        )


if __name__ == "__main__":
    main()
