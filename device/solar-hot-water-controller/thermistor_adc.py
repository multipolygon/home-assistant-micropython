def temperature(adc):
    # https://www.wolframalpha.com/input/?i=linear+fit+%7B0%2C62%7D%2C%7B17.6%2C135%7D%2C%7B42.3%2C270%7D%2C%7B63%2C434%7D%2C%7B94.5%2C643%7D
    return (adc - 36.1997) / 6.26956
