import argparse
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import json
from math import comb


def normalize(coefficients):
    coefficients = list(coefficients)
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    return tuple(coefficients)


def add(left, right, sign=1):
    coefficients = [0] * max(len(left), len(right))
    for degree, value in enumerate(left):
        coefficients[degree] += value
    for degree, value in enumerate(right):
        coefficients[degree] += sign * value
    return normalize(coefficients)


def multiply(left, right):
    coefficients = [0] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            coefficients[left_degree + right_degree] += left_value * right_value
    return normalize(coefficients)


def shift(coefficients, amount):
    return normalize((0,) * amount + tuple(coefficients))


@lru_cache(maxsize=None)
def gaussian(upper, lower):
    if lower < 0 or lower > upper:
        return (0,)
    if lower == 0 or lower == upper:
        return (1,)
    return add(gaussian(upper - 1, lower),
               shift(gaussian(upper - 1, lower - 1), upper - lower))


def product(upper, lower):
    coefficients = (1,)
    for top, bottom in zip(upper, lower):
        coefficients = multiply(coefficients, gaussian(top, bottom))
    return coefficients


def determinant(lower, upper):
    direct = product(upper, lower)
    reversed_product = product(upper, tuple(reversed(lower)))
    return add(direct, reversed_product, -1), direct


def coefficient(coefficients, degree):
    return coefficients[degree] if 0 <= degree < len(coefficients) else 0


def almost_palindromic(coefficients):
    nonzero = tuple(value for value in coefficients if value != 0)
    return nonzero == tuple(reversed(nonzero))


def check_endpoints(lower, upper, coefficients):
    width = len(lower)
    slack = upper[0] - lower[-1]
    first_degree = slack + 1
    count = width if lower[0] > 0 else width - 1
    top_degree = sum(bottom * (top - bottom) for bottom, top in zip(lower, upper))
    assert all(coefficient(coefficients, degree) == 0 for degree in range(first_degree))
    assert coefficient(coefficients, first_degree) == 1
    assert coefficient(coefficients, first_degree + 1) == count + 1
    assert len(coefficients) - 1 == top_degree
    assert coefficient(coefficients, top_degree) == 1
    assert coefficient(coefficients, top_degree - 1) == count
    assert top_degree >= slack + 4
    assert not almost_palindromic(coefficients)
    assert almost_palindromic(shift(coefficients, 7)) is False


def check_gaussians(maximum):
    checked = 0
    for upper in range(maximum + 1):
        for lower in range(upper + 1):
            coefficients = gaussian(upper, lower)
            enumerated = [0] * (lower * (upper - lower) + 1)
            for selected in combinations(range(upper), lower):
                enumerated[sum(selected) - lower * (lower - 1) // 2] += 1
            assert coefficients == tuple(enumerated)
            assert coefficients == tuple(reversed(coefficients))
            assert coefficients[0] == coefficients[-1] == 1
            checked += 1
    return checked


def check_higher_widths(maximum):
    counts = {}
    for width in range(3, 7):
        checked = 0
        for upper in combinations(range(maximum + 1), width):
            for lower in combinations(range(upper[0] + 1), width):
                coefficients, direct = determinant(lower, upper)
                check_endpoints(lower, upper, coefficients)
                checked += 1
        counts[str(width)] = checked
    return counts


def check_width_two(maximum):
    records = []
    for final_upper in range(2, maximum + 1):
        total = 0
        asymmetric = 0
        for first_upper in range(1, final_upper):
            upper = (first_upper, final_upper)
            for lower in combinations(range(first_upper + 1), 2):
                coefficients, direct = determinant(lower, upper)
                lower_gap = lower[1] - lower[0]
                upper_gap = upper[1] - upper[0]
                expected = min(lower_gap, upper_gap) == 1
                assert almost_palindromic(coefficients) == expected
                if expected:
                    first_degree = first_upper - lower[1] + 1
                    other_gap = max(lower_gap, upper_gap)
                    left = add(coefficients, shift(coefficients, first_degree + other_gap), -1)
                    right = shift(add(direct, shift(direct, other_gap), -1), first_degree)
                    assert left == right
                    assert coefficients[first_degree:] == tuple(reversed(coefficients[first_degree:]))
                else:
                    check_endpoints(lower, upper, coefficients)
                    asymmetric += 1
                total += 1
        expected_asymmetric = comb(final_upper - 1, 3) if final_upper >= 4 else 0
        assert total == comb(final_upper + 1, 3)
        assert asymmetric == expected_asymmetric
        ratio = Fraction(asymmetric, total)
        assert ratio == Fraction((final_upper - 2) * (final_upper - 3), final_upper * (final_upper + 1))
        records.append({"lambda": final_upper, "total": total, "not_almost_palindromic": asymmetric,
                        "ratio": str(ratio)})
    return records


def dilate(coefficients, dilation):
    values = [0] * ((len(coefficients) - 1) * dilation + 1)
    for degree, value in enumerate(coefficients):
        values[degree * dilation] = value
    return tuple(values)


@lru_cache(maxsize=None)
def base_factor(length, base):
    values = (1,)
    for index in range(1, length + 1):
        factor = [0] * ((base - 1) * index + 1)
        for exponent in range(base):
            factor[exponent * index] = 1
        values = multiply(values, tuple(factor))
    return values


def base_products(lower, upper, base):
    direct = (1,)
    reverse = (1,)
    for bottom, reversed_bottom, top in zip(lower, reversed(lower), upper):
        direct_factor = multiply(dilate(gaussian(top, bottom), base),
                                 base_factor(top - bottom, base))
        reverse_factor = multiply(dilate(gaussian(top, reversed_bottom), base),
                                  base_factor(top - reversed_bottom, base))
        direct = multiply(direct, direct_factor)
        reverse = multiply(reverse, reverse_factor)
    return direct, reverse


def polynomial_power(coefficients, exponent):
    values = (1,)
    for index in range(exponent):
        values = multiply(values, coefficients)
    return values


def check_extensions(maximum):
    base_cases = 0
    weighted_cases = 0
    shifted_cases = 0
    tuple_counts = {}
    for width in range(2, 5):
        for upper in combinations(range(maximum + 1), width):
            for lower in combinations(range(upper[0] + 1), width):
                key = (width, upper[-1])
                tuple_counts[key] = tuple_counts.get(key, 0) + 1
                ordinary_direct = product(upper, lower)
                ordinary_reverse = product(upper, tuple(reversed(lower)))
                gap = len(ordinary_direct) - len(ordinary_reverse)
                paired_gap = sum((lower[-1-index] - lower[index]) *
                                 (upper[-1-index] - upper[index])
                                 for index in range(width // 2))
                assert gap == paired_gap > 0
                for base in range(1, 4):
                    direct, reverse = base_products(lower, upper, base)
                    assert multiply(reverse, ordinary_direct) == multiply(direct, ordinary_reverse)
                    assert len(direct) - len(reverse) == gap
                    assert direct == tuple(reversed(direct))
                    assert reverse == tuple(reversed(reverse))
                    coefficients = add(direct, reverse, -1)
                    expected = width == 2 and min(lower[1] - lower[0], upper[1] - upper[0]) == 1
                    assert almost_palindromic(coefficients) == expected
                    slack = upper[0] - lower[-1]
                    if not expected:
                        count = width if base >= 2 or lower[0] > 0 else width - 1
                        assert coefficients[slack+1:slack+3] == (1, count + 1)
                        assert coefficients[-2:] == (count, 1)
                    else:
                        first_degree = slack + 1
                        assert coefficients[first_degree:] == tuple(reversed(coefficients[first_degree:]))
                    base_cases += 1
                    for exponent in range(gap + 1):
                        left = add(direct, shift(reverse, exponent), -1)
                        right = add(direct, shift(reverse, gap - exponent), -1)
                        padded = left + (0,) * (len(direct) - len(left))
                        assert normalize(tuple(reversed(padded))) == right
                        if exponent in (0, gap):
                            assert almost_palindromic(left) == expected
                        if 2 * exponent == gap:
                            assert almost_palindromic(left)
                        if width >= 3 and exponent in (1, gap - 1):
                            assert not almost_palindromic(left)
                        shifted_cases += 1
                    for weight in [2, 3]:
                        powered = add(polynomial_power(direct, weight),
                                      polynomial_power(reverse, weight), -1)
                        assert powered[slack + 1] == weight
                        assert all(value == 0 for value in powered[:slack + 1])
                        assert powered[-1] == 1
                        assert not almost_palindromic(powered)
                        weighted_cases += 1
    count_records = []
    for width in range(2, 5):
        for final_upper in range(2 * width - 2, maximum + 1):
            actual = tuple_counts.get((width, final_upper), 0)
            assert actual == comb(final_upper + 1, 2 * width - 1)
            count_records.append({'width': width, 'last_upper': final_upper, 'count': actual})
    family_cases = 0
    for final_upper in range(4, 13):
        for base in range(1, 5):
            direct, reverse = base_products((0, 1), (1, final_upper), base)
            values = add(direct, shift(reverse, 1), -1)
            assert almost_palindromic(values) == (base == 1)
            family_cases += 1
    smallest = {}
    for base in [1, 2]:
        direct, reverse = base_products((0, 1), (1, 4), base)
        smallest[str(base)] = list(add(direct, shift(reverse, 1), -1))
    assert smallest['1'] == [1, 0, 1, 1]
    assert smallest['2'] == [1, 1, 2, 4, 4, 5, 6, 6, 5, 5, 4, 2, 2, 1]
    unimodal_cases = 0
    for final_upper in range(2, 13):
        for first_upper in range(1, final_upper):
            values, direct = determinant((0, 1), (first_upper, final_upper))
            assert values == (0,) * first_upper + (1,) * (final_upper - first_upper)
            unimodal_cases += 1
    return {
        'tuple_upper_max': maximum, 'widths': [2, 3, 4], 'constant_bases': [1, 2, 3],
        'constant_base_cases': base_cases, 'weights': [2, 3], 'weighted_cases': weighted_cases,
        'degree_shift_reciprocity_cases': shifted_cases, 'fixed_last_upper_counts': count_records,
        'example_9_65_family': {'lower': [0, 1], 'upper': [1, 4], 'degree_shift': 1,
                          'smallest_coefficients_by_base': smallest,
                          'family_n_range': [4, 12], 'family_base_range': [1, 4],
                          'family_cases': family_cases,
                          'classification': 'for the stated family, almost palindromic iff base=1'},
        'constant_nonzero_sequence_family_cases': unimodal_cases,
    }


def main():
    parser = argparse.ArgumentParser(description="Exact Gaussian coefficient and determinant checks")
    parser.add_argument("--max-upper", type=int, default=10)
    parser.add_argument("--counting-max", type=int, default=18)
    parser.add_argument("--extension-max", type=int, default=6)
    arguments = parser.parse_args()
    assert arguments.max_upper >= 3 and arguments.counting_max >= 4
    gaussian_count = check_gaussians(arguments.max_upper)
    higher_counts = check_higher_widths(arguments.max_upper)
    width_two = check_width_two(arguments.counting_max)
    extensions = check_extensions(arguments.extension_max)
    example, direct = determinant((0, 1, 2), (2, 3, 4))
    result = {
        "arithmetic": "exact integer polynomial coefficients",
        "gaussian_crosscheck": {"upper_max": arguments.max_upper, "cases": gaussian_count,
                                "methods": ["q-Pascal recurrence", "subset exponent enumeration"]},
        "higher_width_endpoints": {"upper_max": arguments.max_upper, "cases_by_width": higher_counts,
                                   "conditions": "0 <= a1 < ... < a_mu <= b1 < ... < b_mu"},
        "width_two": {"final_upper_max": arguments.counting_max,
                      "cases": sum(row["total"] for row in width_two), "counts": width_two,
                      "classification": "almost palindromic iff min(a2-a1,b2-b1)=1"},
        "example": {"a": [0, 1, 2], "b": [2, 3, 4], "coefficients_low_to_high": list(example)},
        "extensions": extensions,
        "coverage": "Finite checks of endpoint formulas, width-two classification, counts, constant bases and weights, degree-shift reciprocity, specified slices of Conjecture 9.66 and the family extending Example 9.65; all-parameter arguments are in note.tex.",
        "status": "all assertions passed",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
