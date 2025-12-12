def req_sqrt(number: float, guess: float = None, iteration: int = 5):
    # İlk tahmin (guess) verilmemişse number/2'den başla
    if guess is None:
        guess = number/2

    # Durdurma koşulu
    if iteration == 0:
        return guess

    new_guess = (guess + number / guess) / 2

    return req_sqrt(number, new_guess, iteration - 1)


sqrt = req_sqrt(657, iteration=100)

print("{} sayısının karesi: {} ".format(sqrt, sqrt*sqrt))

