class Counter:
    """Counter objects can store between 0 and 999."""

    def __init__(self, parent, x, y, n1, n2, n3):
        """Initialises counters."""
        self.parent = parent
        self.x = x
        self.y = y
        self.numbers = [n1, n2, n3]

    def draw(self):
        """Draws the counter on the screen."""
        for i, number in enumerate(self.numbers):
            self.parent.game_display.blit(
                self.parent.images[number], (self.x+(15*i), self.y))

    def increment(self):
        """Increments the total number of the counter."""
        if self.numbers[2] < 9:
            self.numbers[2] += 1
        elif self.numbers[1] < 9:
            self.numbers[1] += 1
            self.numbers[2] = 0
        elif self.numbers[0] < 9:
            self.numbers[0] += 1
            self.numbers[1] = 0
            self.numbers[2] = 0

    def decrement(self):
        """Decrements the total number of the counter."""
        if self.numbers[2] > 0:
            self.numbers[2] -= 1
        elif self.numbers[1] > 0:
            self.numbers[1] -= 1
            self.numbers[2] = 9
        elif self.numbers[0] > 0:
            self.numbers[0] -= 1
            self.numbers[1] = 9
            self.numbers[2] = 9

    def get_val(self):
        """Returns the value of the counter."""
        total_val = self.numbers[0] * 100
        total_val += self.numbers[1] * 10
        total_val += self.numbers[2]
        return total_val

    def set_val(self, aim):
        """Sets the value of the counter"""
        while aim > self.get_val():
            self.increment()
        while self.get_val() > aim:
            self.decrement()
