forsetter=True
while forsetter:
    try:
        if float(input("(a)hoyden din:"))> 119:
            print("Du er hoy nok")
            forsetter=False
        else:
            print("Du er ikke hoy nok")
            forsetter=False
    except ValueError:
            print("tallet er ikke et flyt tall, prøv igjen med tall")    
            