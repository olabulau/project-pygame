class Tile:
    """Tile objects make up the game grid."""

    def __init__(self, parent, x, y):
        """Initialise tiles."""
        self.parent = parent
        self.x = x
        self.y = y
        self.adj = 0
        self.covered = True
        self.flagged = False
        self.mine = False
        self.exploded = False
        self.unsure = False

    def draw(self):
        if self.unsure:
            sprite = self.parent.images["QUESTION"]
        elif self.flagged:
            sprite = self.parent.images["FLAGGED"]
        elif self.covered and not self.parent.won:
            sprite = self.parent.images["COVERED"]
        elif self.exploded:
            sprite = self.parent.images["EXPLODED"]
        elif self.mine:
            sprite = self.parent.images["MINE"]
        elif self.adj > 0:
            sprite = self.parent.images["T_" + str(self.adj)]
        else:
            sprite = self.parent.images["UNCOVERED"]

        self.parent.game_display.blit(sprite, (self.x, self.y))
