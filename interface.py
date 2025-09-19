import pygame
from typing import Callable

class Button:
    """An interactable button which triggers in-game events when clicked

    Attributes:
        - x (float): The x-coordinate of the button center.
        - y (float): The y-coordinate of the button center.
        - font (pygame.font.Font): Font used to render text.
        - base_colour (str): Default colour of the text.
        - hover_colour (str): Text colour when mouse hovers over the button.
        - text_input (str): The label text of the button.
        - text (pygame.Surface): Rendered text surface.
        - image (pygame.Surface): Button background surface.
        - rect (pygame.Rect): Rect for button positioning and collision detection.
        - text_rect (pygame.Rect): Rect for positioning text over button.
        - action (Callable): Function called when the button is clicked.
    """
    x: float
    y: float
    font: pygame.font.Font
    base_colour: str
    hover_colour: str
    text_input: str
    text: pygame.Surface
    image: pygame.Surface
    rect: pygame.rect
    text_rect: pygame.rect
    action: Callable
    def __init__(self, pos: tuple[float, float], text_input: str,
                 font: pygame.font.Font, base_colour: str, hover_colour: str,
                 action: Callable) -> None:
        """Initialize a Button at <pos> which displays <text_input> in font
        <font>. The button is <base_colour> or <hover_colour> based on
        whether the user is hovering over it and runs <action> when pressed.
        """
        self.x = pos[0]
        self.y = pos[1]
        self.font = font
        self.base_colour = base_colour
        self.hover_colour = hover_colour
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_colour)
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
        """Return true if <position> is inside <self>.rect"""
        return self.rect.collidepoint(position)

    def change_colour(self, position: tuple[float, float]) -> None:
        """Change colour of <self> based on whether <position> is inside
        <self>.rect.
        """
        if self.check_for_input(position):
            self.text = self.font.render(self.text_input, True, self.hover_colour, None)
        else:
            self.text = self.font.render(self.text_input, True, self.base_colour, None)


class ScrollArea:
    """A scrollable viewport area that displays content larger than its size.

    Attributes:
        - rect (pygame.Rect): The visible area of the scroll area.
        - content_height (int): Height of the content inside the scroll area.
        - scroll_y (int): Current vertical scroll offset.
        - scroll_speed (int): Pixels to scroll per scroll action.
        - bg_colour (tuple[int, int, int]): Background colour.
        - surface (pygame.Surface): Surface to render content onto.
        - scrollbar_colour (tuple[int, int, int]): Default scrollbar colour.
        - scrollbar_hover_colour (tuple[int, int, int]): Scrollbar colour when dragged.
        - dragging (bool): True if the scrollbar is currently being dragged.
        - drag_offset (int): Distance from mouse to top of scrollbar when dragging.
    """
    rect: pygame.Rect
    content_height: int
    scroll_y: int
    scroll_speed: int
    bg_colour: tuple[int, int, int]
    surface: pygame.Surface
    scrollbar_colour: tuple[int, int, int]
    scrollbar_hover_colour: tuple[int, int, int]
    dragging: bool
    drag_offset: int
    def __init__(self, x, y, width, height, content_height) -> None:
        """Initialize a ScrollArea at <x>, <y> with a viewport of <width> by
        <height>. The ScrollArea has a total height of <content_height>.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.content_height = content_height
        self.scroll_y = 0
        self.scroll_speed = 30
        self.bg_colour = (255, 255, 255)
        self.surface = pygame.Surface((width, max(height, content_height)))
        self.scrollbar_colour = (180, 180, 180)
        self.scrollbar_hover_colour = (140, 140, 140)
        self.dragging = False
        self.drag_offset = 0

    def scroll_up(self) -> None:
        """Move the view up, limiting to content bounds."""
        if self.content_height > self.rect.height:
            self.scroll_y = max(0, self.scroll_y - self.scroll_speed)

    def scroll_down(self) -> None:
        """Move the view down, limiting to content bounds."""
        if self.content_height > self.rect.height:
            max_scroll = self.content_height - self.rect.height
            self.scroll_y = min(max_scroll, self.scroll_y + self.scroll_speed)

    def handle_event(self, event):
        """Handle mouse <event> to scroll content or drag the scrollbar."""
        if self.content_height <= self.rect.height:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_up()
            elif event.button == 5:
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

    def _scrollbar_rect(self) -> pygame.Rect:
        """Return the current scrollbar rect based on scroll position."""
        if self.content_height <= self.rect.height:
            return pygame.Rect(0, 0, 0, 0)
        ratio = self.rect.height / self.content_height
        scrollbar_height = int(self.rect.height * ratio)
        scrollbar_y = self.rect.y + int(self.scroll_y * (self.rect.height - scrollbar_height) / (self.content_height - self.rect.height))
        return pygame.Rect(self.rect.right - 8, scrollbar_y, 6, scrollbar_height)

    def draw(self, screen) -> None:
        """Draw <self> on <screen>."""
        view = pygame.Surface((self.rect.width, self.rect.height))
        view.blit(self.surface, (0, -self.scroll_y))
        screen.blit(view, self.rect.topleft)
        pygame.draw.rect(screen, "Black", self.rect, 2)

        if self.content_height > self.rect.height:
            scrollbar_rect = self._scrollbar_rect()
            colour = self.scrollbar_hover_colour if self.dragging else self.scrollbar_colour
            pygame.draw.rect(screen, colour, scrollbar_rect, border_radius=3)

    def get_surface(self) -> pygame.Surface:
        """Return <self>'s surface, which contains all scrollable content."""
        return self.surface
