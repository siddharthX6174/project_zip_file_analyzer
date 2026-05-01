def print_star_pattern(n):
    """
    Prints a star pattern of size n.
    
    :param n: The height and width of the star pattern (should be an odd number).
    """
    if n % 2 == 0:
        raise ValueError("The size of the pattern should be an odd number.")
    
    mid = n // 2
    
    for i in range(n):
        for j in range(n):
            if i == mid or j == mid or i + j == mid or i - j == mid or j - i == mid or i + j == n - 1 + mid:
                print('*', end='')
            else:
                print(' ', end='')
        print()

if __name__ == "__main__":
    size = int(input("Enter the size of the star pattern (odd number): "))
    print_star_pattern(size)
