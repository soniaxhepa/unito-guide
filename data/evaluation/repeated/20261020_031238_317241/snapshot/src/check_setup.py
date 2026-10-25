from importlib.metadata import version


PACKAGES = [
    "requests",
    "beautifulsoup4",
    "PyMuPDF",
    "pytest",
]


def main():
    print("Ambiente UniTO Guide configurato correttamente.\n")

    for package in PACKAGES:
        print(f"{package}: {version(package)}")


if __name__ == "__main__":
    main()