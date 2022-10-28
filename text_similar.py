from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
    a = "제러콜라"
    b = "제로골라"
    similarity = similar(a, b)
    print(similarity)