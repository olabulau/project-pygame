import pygame
import time


class TextBox:
    """TextBox objects store text typed by the user."""

    def __init__(self, x, y, w, h, limit=3):
        """Initialise tiles."""
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.value = ""
        self.limit = limit

    def get_val(self):
        """Returns the value of the TextBox."""
        return self.value

    def key_response(self, event):
        """Either deletes letter or adds letter to value."""
        if event.key == pygame.K_BACKSPACE:
            if len(self.value) > 0:
                self.value = self.value[:-1]
        else:
            if not self.too_big():
                self.value += event.unicode
                self.value = self.value.upper()

    def too_big(self):
        """Returns true if the value has reached the assigned limit."""
        if len(self.value) < self.limit:
            return False
        else:
            return True

    def draw(self, parent):
        """Draws the TextBox to the screen."""

        # Draw white background over whole screen
        background = pygame.Rect(0, 0, parent.W_WIDTH, parent.W_HEIGHT)
        pygame.draw.rect(parent.game_display, (255, 255, 255), background)

        # Draw text box
        back_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(parent.game_display, (0, 0, 0), back_rect)

        # Draw text input
        img = parent.font.render(self.value, True, (255, 255, 255))
        rect = img.get_rect()
        rect.topleft = (self.x+10, self.y+10)
        parent.game_display.blit(img, rect)

        # Draw caption on box
        font = pygame.font.SysFont(None, 25)
        caption = font.render("Please enter name:", True, (0, 0, 0))
        caption_rect = pygame.Rect(
            (rect.topleft[0]-55, rect.topleft[1]-30), (self.w, self.h))
        parent.game_display.blit(caption, caption_rect)

        # Blink cursor every half second unless box full
        if time.time() % 1 > 0.5 and not self.too_big():
            cursor = pygame.Rect(
                (rect.bottomright[0], rect.bottomright[1]-5), (12, 2))
            pygame.draw.rect(parent.game_display, (255, 255, 255), cursor)
