# 基本入力テンプレート
import sys

input = sys.stdin.readline
sys.setrecursionlimit(10**6)


def read_int():
    return int(input())


def read_ints():
    return list(map(int, input().split()))


def read_str():
    return input().rstrip("\n")


def main():
    n = read_int()
    a = read_ints()
    print(sum(a))


main()
