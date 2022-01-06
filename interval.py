from math import isclose


class Interval:
    mid: float
    rad: float

    def __init__(self, mid: float, rad: float):
        self._mid = mid
        self._rad = rad

    @property
    def mid(self) -> float:
        return self._mid

    @property
    def rad(self) -> float:
        return self._rad

    @property
    def min(self) -> float:
        return self._mid - self._rad

    @property
    def max(self) -> float:
        return self._mid + self._rad

    def __eq__(self, other) -> bool:
        if isinstance(other, Interval):
            return bool(isclose(self._mid, other._mid) and isclose(self._rad, other._rad))
        raise TypeError(f"unsupported operand type(s) for ==: 'Interval' and '{type(other).__name__}'")

    def __add__(self, other) -> 'Interval':
        if isinstance(other, Interval):
            return Interval(self._mid + other._mid, self._rad + other._rad)
        raise TypeError(f"unsupported operand type(s) for +: 'Interval' and '{type(other).__name__}'")

    def __sub__(self, other) -> 'Interval':
        if isinstance(other, Interval):
            return Interval(self._mid - other._mid, self._rad + other._rad)
        raise TypeError(f"unsupported operand type(s) for +: 'Interval' and '{type(other).__name__}'")

    def __mul__(self, other) -> 'Interval':
        if isinstance(other, float) or isinstance(other, int):
            return Interval(self._mid * other, self._rad * other)
        elif isinstance(other, Interval):
            minmin = self.min * other.min
            minmax = self.min * other.max
            maxmin = self.max * other.min
            maxmax = self.max * other.max
            min_ = min(minmin, minmax, maxmin, maxmax)
            max_ = max(minmin, minmax, maxmin, maxmax)
            return Interval((min_ + max_) / 2., (max_ - min_) / 2.)
        raise TypeError(f"unsupported operand type(s) for *: 'Interval' and '{type(other).__name__}'")

    def __truediv__(self, other) -> 'Interval':
        if isinstance(other, float) or isinstance(other, int):
            return Interval(self._mid / other, self._rad / other)
        elif isinstance(other, Interval):
            min_ = 1. / other.max
            max_ = 1. / other.min
            return self * Interval((min_ + max_) / 2., (max_ - min_) / 2.)
        raise TypeError(f"unsupported operand type(s) for /: 'Interval' and '{type(other).__name__}'")

    def __contains__(self, item) -> bool:
        if isinstance(item, float) or isinstance(item, int):
            min_, max_ = self.min, self.max
            return min_ <= item <= max_ or isclose(item, min_) or isclose(item, max_)
        raise TypeError(f"'in <Interval>' requires float or int as left operand, not {type(item).__name__}")

    def __repr__(self):
        return '[{:g}, {:g}], {:g} ± {:g}'.format(self.min, self.max, self._mid, self._rad)

    def distance_to(self, other: 'Interval') -> float:
        return max(abs(self.min - other.min), abs(self.max - other.max))
