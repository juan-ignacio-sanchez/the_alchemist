import pygame


def create_fonts(font_sizes_list):
    """Creates different fonts with one list"""
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts


def render(fnt, what, color, where, screen):
    """Renders the fonts as passed from display_fps"""
    text_to_show = fnt.render(what, 0, pygame.Color(color))
    return screen.blit(text_to_show, where)


def display_fps(clock, screen):
    """Data that will be rendered and blitted in _display"""
    fonts = create_fonts([32, 16, 14, 8])
    return render(
        fonts[0],
        what=str(int(clock.get_fps())),
        color="white",
        where=(0, 0),
        screen=screen,
    )
