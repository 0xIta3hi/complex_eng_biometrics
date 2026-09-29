"""Run one toy authentication request against the three party processes."""

from .protocol import authenticate


def main() -> None:
    result = authenticate([12, 5, 9, 3], [10, 7, 8, 4], threshold=8)
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
