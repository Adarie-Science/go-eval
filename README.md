# Datasets

`examples/set0.jsonl`: This is a small dataset to be used for integration testing (i.e. making sure the eval setup is working) -- not to be used as a model eval.

# Script usage examples

- `python generate_data.py 30 examples/myset.jsonl` -- Generate 30 test cases and save to `examples/myset.jsonl`

- `python quiz.py examples/myset.jsonl 10` -- Quiz the user (i.e. presumably a human) on 10 test cases previously saved to `examples/myset.jsonl`
