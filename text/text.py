import pygame


def _render(fnt, what, color, where, screen):
    """Renders the fonts as passed from display_fps"""
    text_to_show = fnt.render(what, 0, pygame.Color(color))
    return screen.blit(text_to_show, where)


def _create_fonts(font_sizes_list):
    """Creates different fonts with one list"""
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts


def display_fps(clock, screen):
    """Data that will be rendered and blitted in _display"""
    fonts = _create_fonts([32, 16, 14, 8])
    return _render(
        fonts[0],
        what=str(int(clock.get_fps())),
        color="white",
        where=(0, 0),
        screen=screen,
    )


def show_score(score: str, screen: pygame.Surface):
    return _render(
        fnt=pygame.font.SysFont("Bitstream Vera", 40),
        what=score,
        color="white",
        where=(5, screen.get_height() - 32),
        screen=screen,
    )
