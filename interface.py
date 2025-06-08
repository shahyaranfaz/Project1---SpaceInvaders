import pygame
from typing import Callable

class Button:
    """An interactable button which triggers in-game events."""
    def __init__(self, pos: tuple[float, float], text_input: str,
                 font: pygame.font.Font, base_color: str, hover_color: str,
                 action: Callable) -> None:
        self.x = pos[0]
        self.y = pos[1]
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if "Q" in text_input:
            text_rect = self.text.get_rect()
        else:
            text_rect = self.text.get_bounding_rect()
        self.image = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.text_rect = self.text.get_rect(center=(self.x, self.y))
        self.action = action

    def draw(self, screen) -> None:
        """Draws <self> on <screen>."""
        if self.image:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_for_input(self, position: tuple[float, float]) -> bool:
        """Return true if position is inside <self>.rect"""
        return self.rect.collidepoint(position)

    def change_color(self, position: tuple[float, float]) -> None:
        """Change color of <self> based on whether position is inside
        <self>.rect.
        """
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hover_color, None)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color, None)


class ScrollArea:
    def __init__(self, x, y, width, height, content_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_height = content_height
        self.scroll_y = 0
        self.scroll_speed = 30
        self.bg_color = (255, 255, 255)
        self.surface = pygame.Surface((width, max(height, content_height)))
        self.scrollbar_color = (180, 180, 180)
        self.scrollbar_hover_color = (140, 140, 140)
        self.dragging = False
        self.drag_offset = 0

    def scroll_up(self):
        if self.content_height > self.rect.height:  # <-- prevent scroll
            self.scroll_y = max(0, self.scroll_y - self.scroll_speed)

    def scroll_down(self):
        if self.content_height > self.rect.height:  # <-- prevent scroll
            max_scroll = self.content_height - self.rect.height
            self.scroll_y = min(max_scroll, self.scroll_y + self.scroll_speed)

    def handle_event(self, event):
        if self.content_height <= self.rect.height:
            return  # <-- skip handling events if no scrolling needed

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_up()
            elif event.button == 5:  # Scroll down
                self.scroll_down()
            elif event.button == 1:
                if self._scrollbar_rect().collidepoint(event.pos):
                    self.dragging = True
                    self.drag_offset = event.pos[1] - self._scrollbar_rect().y

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            scrollbar = self._scrollbar_rect()
            rel_y = event.pos[1] - self.drag_offset - self.rect.y
            rel_y = max(0, min(rel_y, self.rect.height - scrollbar.height))
            scroll_ratio = rel_y / (self.rect.height - scrollbar.height)
            self.scroll_y = int(scroll_ratio * (self.content_height - self.rect.height))

    def _scrollbar_rect(self):
        if self.content_height <= self.rect.height:
            return pygame.Rect(0, 0, 0, 0)
        ratio = self.rect.height / self.content_height
        scrollbar_height = int(self.rect.height * ratio)
        scrollbar_y = self.rect.y + int(self.scroll_y * (self.rect.height - scrollbar_height) / (self.content_height - self.rect.height))
        return pygame.Rect(self.rect.right - 8, scrollbar_y, 6, scrollbar_height)

    def draw(self, screen):
        view = pygame.Surface((self.rect.width, self.rect.height))
        view.blit(self.surface, (0, -self.scroll_y))
        screen.blit(view, self.rect.topleft)
        pygame.draw.rect(screen, "Black", self.rect, 2)

        if self.content_height > self.rect.height:
            scrollbar_rect = self._scrollbar_rect()
            color = self.scrollbar_hover_color if self.dragging else self.scrollbar_color
            pygame.draw.rect(screen, color, scrollbar_rect, border_radius=3)

    def get_surface(self):
        return self.surface
