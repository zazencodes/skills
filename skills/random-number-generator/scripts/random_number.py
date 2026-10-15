#!/usr/bin/env python3
"""Random number CLI for the random-number-generator skill."""

import argparse
import json
import random
import secrets
import sys
from typing import Any, List, Optional, Union


class UsageError(ValueError):
    """Raised when CLI input is syntactically valid but semantically invalid."""


def parse_json_list(raw: str, name: str) -> List[Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UsageError(f"{name} must be valid JSON: {exc.msg}") from exc
    if not isinstance(value, list):
        raise UsageError(f"{name} must be a JSON list")
    return value


def validate_range(low: Union[int, float], high: Union[int, float]) -> None:
    if low > high:
        raise UsageError(f"low ({low}) must be <= high ({high})")


def validate_non_negative_int(value: int, name: str) -> None:
    if value < 0:
        raise UsageError(f"{name} must be non-negative, got {value}")


def validate_list_not_empty(items: List[Any], name: str) -> None:
    if not items:
        raise UsageError(f"{name} cannot be empty")


def validate_weights(
    population: List[Any], weights: List[Any]
) -> List[Union[int, float]]:
    if len(weights) != len(population):
        raise UsageError(
            f"weights length ({len(weights)}) must match population length ({len(population)})"
        )
    numeric_weights: List[Union[int, float]] = []
    for index, weight in enumerate(weights):
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise UsageError(f"weights[{index}] must be numeric")
        numeric_weights.append(weight)
    return numeric_weights


def random_int(args: argparse.Namespace) -> List[int]:
    validate_range(args.low, args.high)
    validate_non_negative_int(args.size, "size")
    return [random.randint(args.low, args.high) for _ in range(args.size)]


def random_float(args: argparse.Namespace) -> List[float]:
    validate_range(args.low, args.high)
    validate_non_negative_int(args.size, "size")
    return [random.uniform(args.low, args.high) for _ in range(args.size)]


def random_choices(args: argparse.Namespace) -> List[Any]:
    population = parse_json_list(args.population_json, "population-json")
    validate_list_not_empty(population, "population")
    validate_non_negative_int(args.k, "k")
    weights = None
    if args.weights_json is not None:
        raw_weights = parse_json_list(args.weights_json, "weights-json")
        weights = validate_weights(population, raw_weights)
    return random.choices(population, weights=weights, k=args.k)


def random_shuffle(args: argparse.Namespace) -> List[Any]:
    items = parse_json_list(args.items_json, "items-json")
    validate_list_not_empty(items, "items")
    return random.sample(items, len(items))


def random_sample(args: argparse.Namespace) -> List[Any]:
    population = parse_json_list(args.population_json, "population-json")
    validate_list_not_empty(population, "population")
    validate_non_negative_int(args.k, "k")
    if args.k > len(population):
        raise UsageError("sample size k cannot be greater than population size")
    return random.sample(population, args.k)


def secure_token_hex(args: argparse.Namespace) -> List[str]:
    validate_non_negative_int(args.nbytes, "nbytes")
    validate_non_negative_int(args.size, "size")
    return [secrets.token_hex(args.nbytes) for _ in range(args.size)]


def secure_random_int(args: argparse.Namespace) -> List[int]:
    if args.upper_bound <= 0:
        raise UsageError("upper-bound must be positive")
    validate_non_negative_int(args.size, "size")
    return [secrets.randbelow(args.upper_bound) for _ in range(args.size)]


def add_raw(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--raw",
        action="store_true",
        help="print scalar results without JSON string quoting",
    )


def add_size(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--size",
        type=int,
        default=1,
        help="number of items to generate, default 1",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate random numbers, choices, shuffles, samples, and secure tokens "
            "using Python standard library modules."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser(
        "random-int",
        aliases=["random_int", "int"],
        help="generate random integer(s) between inclusive bounds",
    )
    p.add_argument("--low", type=int, required=True, help="inclusive lower bound")
    p.add_argument("--high", type=int, required=True, help="inclusive upper bound")
    add_size(p)
    add_raw(p)
    p.set_defaults(func=random_int)

    p = subparsers.add_parser(
        "random-float",
        aliases=["random_float", "float"],
        help="generate random float(s) between low and high",
    )
    p.add_argument("--low", type=float, default=0.0, help="lower bound, default 0.0")
    p.add_argument("--high", type=float, default=1.0, help="upper bound, default 1.0")
    add_size(p)
    add_raw(p)
    p.set_defaults(func=random_float)

    p = subparsers.add_parser(
        "random-choices",
        aliases=["random_choices", "choices"],
        help="choose k items from a population with replacement",
    )
    p.add_argument("--population-json", required=True, help="JSON list of items")
    p.add_argument("--k", type=int, default=1, help="number of choices, default 1")
    p.add_argument("--weights-json", help="optional JSON list of numeric weights")
    add_raw(p)
    p.set_defaults(func=random_choices)

    p = subparsers.add_parser(
        "random-shuffle",
        aliases=["random_shuffle", "shuffle"],
        help="return a new list with items in random order",
    )
    p.add_argument("--items-json", required=True, help="JSON list of items")
    add_raw(p)
    p.set_defaults(func=random_shuffle)

    p = subparsers.add_parser(
        "random-sample",
        aliases=["random_sample", "sample"],
        help="choose k unique items without replacement",
    )
    p.add_argument("--population-json", required=True, help="JSON list of items")
    p.add_argument("--k", type=int, required=True, help="sample size")
    add_raw(p)
    p.set_defaults(func=random_sample)

    p = subparsers.add_parser(
        "secure-token-hex",
        aliases=["secure_token_hex", "token-hex"],
        help="generate cryptographically secure hex token(s)",
    )
    p.add_argument(
        "--nbytes",
        type=int,
        default=32,
        help="number of random bytes before hex encoding, default 32",
    )
    add_size(p)
    add_raw(p)
    p.set_defaults(func=secure_token_hex)

    p = subparsers.add_parser(
        "secure-random-int",
        aliases=["secure_random_int", "secure-int"],
        help="generate secure integer(s) in range [0, upper-bound)",
    )
    p.add_argument("--upper-bound", type=int, required=True, help="exclusive upper bound")
    add_size(p)
    add_raw(p)
    p.set_defaults(func=secure_random_int)

    return parser


def emit(value: Any, raw: bool) -> None:
    if raw and not isinstance(value, (list, dict)):
        print(value)
        return
    print(json.dumps(value, ensure_ascii=False))


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except UsageError as exc:
        parser.exit(2, f"error: {exc}\n")
    except ValueError as exc:
        parser.exit(2, f"error: {exc}\n")
    emit(result, args.raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
