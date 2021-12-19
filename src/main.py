import random


def get_measures(amount: int, mean, sigma):
    return [random.gauss(mean, sigma) for _ in range(amount)]


def expenctancy(values):
    """
    this is only sort of an expenctancy.
    Indeed, although it enventually performs the correct calculation
    it makes use of the specific formula used in this scenario to optimize away the very notion of probability.
    This whole simplification process brings it down to a simple weighted average.
    """
    return sum(values) / len(values)


def variance(values):
    """
    Just as the formula for the expenctancy was greatly simplified it is found
    that the variance of the power of the signal is extremely simple. Indeed the power's
    formula depends on none but one random variable. Since V[aX+b]=a^2E[X] and a=1 here
    hence the variance of the power is simply the expectancy
    """
    return expenctancy(values)


def main():
    print("all is well")


# TODO build an example dict for the esp8266 as a mind-note


def read_csv(file_name):
    pass


def sqrt(value):
    pass


def path_loss_params_estimation(s1, s2):
    pass


if __name__ == "__main__":
    main()
