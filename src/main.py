import pygame
import sys

pygame.init()
info = pygame.display.Info()

BOARD_SIZE = 12
MARGIN = 40
BOTTOM_PANEL = 80

available_w = info.current_w - 100
available_h = info.current_h - 150 - BOTTOM_PANEL

CELL = min(available_w, available_h) // BOARD_SIZE

WINDOW_W = BOARD_SIZE * CELL + 2 * MARGIN
WINDOW_H = BOARD_SIZE * CELL + 2 * MARGIN + BOTTOM_PANEL
PIECE_SIZE = CELL - 8
INNER_SIZE = PIECE_SIZE - 6

print(f"Экран: {info.current_w}x{info.current_h}, CELL={CELL}, окно={WINDOW_W}x{WINDOW_H}")

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
SELECTED = (0, 255, 0)
MOVE_DOT = (0, 200, 0)
CAPTURE_RING = (255, 0, 0)
EN_PASSANT_RING = (255, 165, 0)
DOUBLE_DOT = (255, 200, 0)
CHECK_COLOR = (255, 0, 0)
WIN_COLOR = (255, 215, 0)

OUTLINE_COLORS = {'w': (0, 0, 0), 'b': (255, 255, 255)}
PLAYER_COLORS = {'w': (200, 220, 255), 'b': (255, 150, 150)}
PLAYER_LABELS = {'w': 'Белые', 'b': 'Чёрные'}
TURN_ORDER = ['w', 'b']
PROMOTION_CHOICES = ['Q', 'R', 'B', 'N']
PAWN_FORWARD = {'w': (0, +1), 'b': (0, -1)}
PAWN_PROMOTION_LINE = {'w': 11, 'b': 0}


def is_enemy(c1, c2):
    return c1 != c2


def add_outline(image, outline_color=(0, 0, 0), thickness=2):
    mask = pygame.mask.from_surface(image)
    outline = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    result = pygame.Surface((image.get_width() + thickness * 2,
                             image.get_height() + thickness * 2), pygame.SRCALPHA)
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            result.blit(outline, (thickness + dx, thickness + dy))
    result.blit(image, (thickness, thickness))
    return result


def load_pieces():
    pieces = {}
    types = ['K', 'Q', 'R', 'B', 'N', 'P']
    base_pieces = {}

    for base, prefix in [('white', 'w'), ('black', 'b')]:
        for symbol in types:
            path = f"images/pieces/{prefix}{symbol}.png"
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (INNER_SIZE, INNER_SIZE))
                base_pieces[(base, symbol)] = img
            except pygame.error as e:
                print(f"Не найден файл: {path} — {e}")
                surf = pygame.Surface((INNER_SIZE, INNER_SIZE), pygame.SRCALPHA)
                color = (255, 255, 255) if base == 'white' else (0, 0, 0)
                pygame.draw.circle(surf, color, (INNER_SIZE // 2, INNER_SIZE // 2),
                                   INNER_SIZE // 2 - 2)
                base_pieces[(base, symbol)] = surf

    for base, prefix in [('white', 'w'), ('black', 'b')]:
        path2 = f"images/pieces/{prefix}N2.png"
        try:
            img2 = pygame.image.load(path2).convert_alpha()
            w, h = img2.get_size()
            scale = min(INNER_SIZE / w, INNER_SIZE / h)
            img2 = pygame.transform.smoothscale(img2, (int(w * scale), int(h * scale)))
            base_pieces[(base, 'N2')] = img2
        except pygame.error as e:
            print(f"Не найден файл: {path2} — {e} (использую обычного коня)")
            base_pieces[(base, 'N2')] = base_pieces[(base, 'N')]

    for base, prefix in [('white', 'w'), ('black', 'b')]:
        path_r2 = f"images/pieces/{prefix}R2.png"
        try:
            img_r2 = pygame.image.load(path_r2).convert_alpha()
            w, h = img_r2.get_size()
            scale = min(INNER_SIZE / w, INNER_SIZE / h) * 1.0
            img_r2 = pygame.transform.smoothscale(img_r2, (int(w * scale), int(h * scale)))
            base_pieces[(base, 'R2')] = img_r2
        except pygame.error as e:
            print(f"Не найден файл: {path_r2} — {e} (использую обычную ладью)")
            base_pieces[(base, 'R2')] = base_pieces[(base, 'R')]

    for base, prefix in [('white', 'w'), ('black', 'b')]:
        path_j = f"images/pieces/{prefix}J.png"
        try:
            img_j = pygame.image.load(path_j).convert_alpha()
            w, h = img_j.get_size()
            scale = min(INNER_SIZE / w, INNER_SIZE / h) * 1.2
            img_j = pygame.transform.smoothscale(img_j, (int(w * scale), int(h * scale)))
            base_pieces[(base, 'J')] = img_j
        except pygame.error as e:
            print(f"Не найден файл: {path_j} — {e} (использую ферзя)")
            base_pieces[(base, 'J')] = base_pieces[(base, 'Q')]

    all_symbols = ['K', 'Q', 'R', 'B', 'N', 'P', 'N2', 'R2', 'J']
    for player in ['w', 'b']:
        outline_color = OUTLINE_COLORS[player]
        base = 'white' if player == 'w' else 'black'
        for symbol in all_symbols:
            img = base_pieces[(base, symbol)]
            if symbol == 'R2':
                outlined = add_outline(img, outline_color, thickness=6)
            else:
                outlined = add_outline(img, outline_color, thickness=3)

            if symbol == 'R2':
                w, h = outlined.get_size()
                scale = min(PIECE_SIZE / w, PIECE_SIZE / h) * 1.0
                outlined = pygame.transform.smoothscale(
                    outlined, (int(w * scale), int(h * scale)))
            elif symbol in ('N2', 'J'):
                w, h = outlined.get_size()
                scale_mult = 1.2 if symbol == 'J' else 1.0
                scale = min(PIECE_SIZE / w, PIECE_SIZE / h) * scale_mult
                outlined = pygame.transform.smoothscale(
                    outlined, (int(w * scale), int(h * scale)))
            else:
                outlined = pygame.transform.smoothscale(outlined, (PIECE_SIZE, PIECE_SIZE))
            pieces[(player, symbol)] = outlined
    return pieces


def get_piece_image(pieces, color, typ):
    return pieces[(color, typ)]


def initial_position():
    pos = {}

    # --- БЕЛЫЕ ---
    # 1-я горизонталь
    pos[(3, 0)] = ('w', 'R2')   # d1 — гепард
    pos[(4, 0)] = ('w', 'N2')   # e1 — орёл
    pos[(5, 0)] = ('w', 'K')    # f1 — король
    pos[(6, 0)] = ('w', 'J')    # g1 — джинн
    pos[(7, 0)] = ('w', 'N2')   # h1 — орёл
    pos[(8, 0)] = ('w', 'R2')   # i1 — гепард

    # 2-я горизонталь
    pos[(2, 1)] = ('w', 'R')    # c2 — ладья
    pos[(3, 1)] = ('w', 'N')    # d2 — конь
    pos[(4, 1)] = ('w', 'B')    # e2 — слон
    pos[(5, 1)] = ('w', 'Q')    # f2 — ферзь
    pos[(6, 1)] = ('w', 'Q')    # g2 — ферзь
    pos[(7, 1)] = ('w', 'B')    # h2 — слон
    pos[(8, 1)] = ('w', 'N')    # i2 — конь
    pos[(9, 1)] = ('w', 'R')    # j2 — ладья

    # 3-я горизонталь — все пешки
    for c in range(12):
        pos[(c, 2)] = ('w', 'P')

    # --- ЧЁРНЫЕ (зеркально белым) ---
    for (c, r), (color, typ) in list(pos.items()):
        if color == 'w':
            mirror_c = 11 - c
            mirror_r = 11 - r
            pos[(mirror_c, mirror_r)] = ('b', typ)

    return pos


def in_bounds(c, r):
    return 0 <= c < BOARD_SIZE and 0 <= r < BOARD_SIZE


def is_promotion_square_for(color, c, r):
    return r == PAWN_PROMOTION_LINE[color]


def compute_en_passant(position, en_passant_move):
    result = {}
    if en_passant_move is None:
        return result
    fc, fr, tc, tr, pawn_color = en_passant_move
    if (tc, tr) not in position:
        return result
    if position[(tc, tr)][1] != 'P' or position[(tc, tr)][0] != pawn_color:
        return result
    our_color = 'b' if pawn_color == 'w' else 'w'
    our_dc, our_dr = PAWN_FORWARD[our_color]
    enemy_dc, enemy_dr = PAWN_FORWARD[pawn_color]
    for (c, r), (pc, pt) in position.items():
        if pc != our_color or pt != 'P':
            continue
        if enemy_dc == 0:
            if abs(c - fc) != 1:
                continue
            step_dir = 1 if tr > fr else -1
            for mid_r in range(fr + step_dir, tr, step_dir):
                for ddc in [-1, +1]:
                    if c + ddc == fc and r + our_dr == mid_r:
                        if (fc, mid_r) not in position:
                            result[(fc, mid_r)] = (tc, tr)
                        break
        else:
            if abs(r - fr) != 1:
                continue
            step_dir = 1 if tc > fc else -1
            for mid_c in range(fc + step_dir, tc, step_dir):
                for ddr in [-1, +1]:
                    if c + our_dc == mid_c and r + ddr == fr:
                        if (mid_c, fr) not in position:
                            result[(mid_c, fr)] = (tc, tr)
                        break
    return result


def sliding_moves(position, c, r, color, directions):
    moves = []
    for dc, dr in directions:
        nc, nr = c + dc, r + dr
        while in_bounds(nc, nr):
            if (nc, nr) in position:
                if is_enemy(color, position[(nc, nr)][0]):
                    moves.append((nc, nr))
                break
            moves.append((nc, nr))
            nc += dc
            nr += dr
    return moves


def king_moves(position, c, r, color):
    moves = []
    for dc in [-1, 0, 1]:
        for dr in [-1, 0, 1]:
            if dc == 0 and dr == 0:
                continue
            nc, nr = c + dc, r + dr
            if not in_bounds(nc, nr):
                continue
            if (nc, nr) in position:
                if is_enemy(color, position[(nc, nr)][0]):
                    moves.append((nc, nr))
            else:
                moves.append((nc, nr))
    return moves


def knight_moves(position, c, r, color):
    moves = []
    for dc, dr in [(1, 2), (2, 1), (-1, 2), (-2, 1),
                   (1, -2), (2, -1), (-1, -2), (-2, -1)]:
        nc, nr = c + dc, r + dr
        if not in_bounds(nc, nr):
            continue
        if (nc, nr) in position:
            if is_enemy(color, position[(nc, nr)][0]):
                moves.append((nc, nr))
        else:
            moves.append((nc, nr))
    return moves


def two_headed_knight_moves(position, c, r, color):
    moves = []
    for dc, dr in [(1, 3), (3, 1), (-1, 3), (-3, 1),
                   (1, -3), (3, -1), (-1, -3), (-3, -1)]:
        nc, nr = c + dc, r + dr
        if not in_bounds(nc, nr):
            continue
        if (nc, nr) in position:
            if is_enemy(color, position[(nc, nr)][0]):
                moves.append((nc, nr))
        else:
            moves.append((nc, nr))
    return moves


def cheetah_moves(position, c, r, color):
    moves = []
    for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nc, nr = c + dc, r + dr
        jumped = False
        while in_bounds(nc, nr):
            if (nc, nr) in position:
                target_color, target_type = position[(nc, nr)]
                if is_enemy(color, target_color):
                    moves.append((nc, nr))
                    break
                else:
                    if jumped:
                        break
                    jc, jr = nc + dc, nr + dr
                    if not in_bounds(jc, jr):
                        break
                    if (jc, jr) in position:
                        break
                    moves.append((jc, jr))
                    jumped = True
                    break
            else:
                moves.append((nc, nr))
            nc += dc
            nr += dr
    return moves


def cheetah_moves_second(position, c, r, color):
    moves = []
    for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nc, nr = c + dc, r + dr
        while in_bounds(nc, nr):
            if (nc, nr) in position:
                break
            moves.append((nc, nr))
            nc += dc
            nr += dr
    return moves


def genie_moves(position, c, r, color):
    moves = []
    directions = [
        (0, -1), (0, 1), (-1, 0), (1, 0),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    ]
    for dc, dr in directions:
        nc, nr = c + dc, r + dr
        while in_bounds(nc, nr):
            if (nc, nr) in position:
                target_color, target_type = position[(nc, nr)]
                if is_enemy(color, target_color):
                    moves.append((nc, nr))
                    break
                else:
                    jc, jr = nc + dc, nr + dr
                    if not in_bounds(jc, jr):
                        break
                    if (jc, jr) in position:
                        break
                    moves.append((jc, jr))
                    break
            else:
                moves.append((nc, nr))
            nc += dc
            nr += dr
    return moves


def pawn_moves(position, c, r, color, moved_pawns, en_passant_moves):
    moves = []
    dc, dr = PAWN_FORWARD[color]
    on_start = (c, r) not in moved_pawns
    max_steps = 3 if on_start else 2
    for step in range(1, max_steps + 1):
        nc, nr = c + dc * step, r + dr * step
        if not in_bounds(nc, nr):
            break
        if (nc, nr) in position:
            break
        moves.append((nc, nr))
    diagonals = [(-1, dr), (+1, dr)]
    for ddc, ddr in diagonals:
        nc, nr = c + ddc, r + ddr
        if not in_bounds(nc, nr):
            continue
        if (nc, nr) in position:
            if is_enemy(color, position[(nc, nr)][0]):
                moves.append((nc, nr))
    for (tc, tr) in en_passant_moves.keys():
        for ddc, ddr in diagonals:
            if c + ddc == tc and r + ddr == tr:
                moves.append((tc, tr))
                break
    return moves


def get_moves(position, c, r, color, moved_pawns, en_passant_moves):
    if (c, r) not in position:
        return []
    pc, pt = position[(c, r)]
    if pt == 'P':
        return pawn_moves(position, c, r, pc, moved_pawns, en_passant_moves)
    elif pt == 'N':
        return knight_moves(position, c, r, pc)
    elif pt == 'N2':
        return two_headed_knight_moves(position, c, r, pc)
    elif pt == 'R2':
        return cheetah_moves(position, c, r, pc)
    elif pt == 'J':
        return genie_moves(position, c, r, pc)
    elif pt == 'R':
        return sliding_moves(position, c, r, pc,
                             [(0, -1), (0, 1), (-1, 0), (1, 0)])
    elif pt == 'B':
        return sliding_moves(position, c, r, pc,
                             [(-1, -1), (-1, 1), (1, -1), (1, 1)])
    elif pt == 'Q':
        return sliding_moves(position, c, r, pc,
                             [(-1, -1), (-1, 1), (1, -1), (1, 1),
                              (0, -1), (0, 1), (-1, 0), (1, 0)])
    elif pt == 'K':
        return king_moves(position, c, r, pc)
    return []


def find_all_kings(position, color):
    return [(c, r) for (c, r), (pc, pt) in position.items()
            if pc == color and pt == 'K']


def is_square_attacked(position, c, r, by_color):
    for (pc, pr), (color, typ) in position.items():
        if color != by_color:
            continue
        if typ == 'P':
            dc, dr = PAWN_FORWARD[color]
            for ddc, ddr in [(-1, dr), (+1, dr)]:
                if pc + ddc == c and pr + ddr == r:
                    return True
            continue
        if typ == 'N':
            moves = knight_moves(position, pc, pr, color)
        elif typ == 'N2':
            moves = two_headed_knight_moves(position, pc, pr, color)
        elif typ == 'R2':
            moves = cheetah_moves(position, pc, pr, color)
        elif typ == 'J':
            moves = genie_moves(position, pc, pr, color)
        elif typ == 'R':
            moves = sliding_moves(position, pc, pr, color,
                                  [(0, -1), (0, 1), (-1, 0), (1, 0)])
        elif typ == 'B':
            moves = sliding_moves(position, pc, pr, color,
                                  [(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif typ == 'Q':
            moves = sliding_moves(position, pc, pr, color,
                                  [(-1, -1), (-1, 1), (1, -1), (1, 1),
                                   (0, -1), (0, 1), (-1, 0), (1, 0)])
        elif typ == 'K':
            moves = king_moves(position, pc, pr, color)
        else:
            moves = []
        if (c, r) in moves:
            return True
    return False


def has_any_king_attacked(position, color):
    enemy = 'b' if color == 'w' else 'w'
    for kp in find_all_kings(position, color):
        if is_square_attacked(position, kp[0], kp[1], enemy):
            return True
    return False


def is_in_check(position, color):
    return has_any_king_attacked(position, color)


def filter_legal_moves(position, c, r, color, moved_pawns, en_passant_moves):
    moves = get_moves(position, c, r, color, moved_pawns, en_passant_moves)
    legal = []
    for (mc, mr) in moves:
        new_position = dict(position)
        captured = new_position.pop((c, r))
        new_position[(mc, mr)] = captured
        if (mc, mr) in en_passant_moves:
            enemy_pos = en_passant_moves[(mc, mr)]
            if enemy_pos in new_position:
                del new_position[enemy_pos]
        if captured[1] == 'P' and is_promotion_square_for(color, mc, mr):
            new_position[(mc, mr)] = (color, 'Q')
        if not has_any_king_attacked(new_position, color):
            legal.append((mc, mr))
    return legal


def compute_double_moves_cheetah(position, c, r, color, moved_pawns, en_passant_moves):
    first_moves = filter_legal_moves(position, c, r, color, moved_pawns, en_passant_moves)
    double_moves = {}
    for (mc1, mr1) in first_moves:
        if (mc1, mr1) in position:
            continue
        new_pos = dict(position)
        moved = new_pos.pop((c, r))
        new_pos[(mc1, mr1)] = moved
        second_moves = cheetah_moves_second(new_pos, mc1, mr1, color)
        for (mc2, mr2) in second_moves:
            final_pos = dict(new_pos)
            captured2 = final_pos.pop((mc1, mr1))
            final_pos[(mc2, mr2)] = captured2
            if not has_any_king_attacked(final_pos, color):
                if (mc2, mr2) not in first_moves:
                    double_moves[(mc2, mr2)] = (mc1, mr1)
    return first_moves, double_moves


def has_any_legal_move(position, color, moved_pawns, en_passant_moves):
    for (c, r), (pc, pt) in position.items():
        if pc == color:
            if filter_legal_moves(position, c, r, color, moved_pawns, en_passant_moves):
                return True
    return False


def is_checkmate(position, color, moved_pawns, en_passant_moves):
    if not is_in_check(position, color):
        return False
    return not has_any_legal_move(position, color, moved_pawns, en_passant_moves)


# --- Отрисовка ---

def draw_board(screen, font):
    for c in range(BOARD_SIZE):
        for r in range(BOARD_SIZE):
            x = MARGIN + c * CELL
            y = MARGIN + (BOARD_SIZE - 1 - r) * CELL
            rect = pygame.Rect(x, y, CELL, CELL)
            pygame.draw.rect(screen, LIGHT if (c + r) % 2 == 0 else DARK, rect)
    for c in range(BOARD_SIZE):
        letter = chr(ord('a') + c)
        x = MARGIN + c * CELL + CELL // 2
        y = MARGIN + BOARD_SIZE * CELL + 15
        text = font.render(letter, True, (200, 200, 200))
        screen.blit(text, (x - 5, y))
    for r in range(BOARD_SIZE):
        x = MARGIN - 25
        y = MARGIN + (BOARD_SIZE - 1 - r) * CELL + CELL // 2
        text = font.render(str(r + 1), True, (200, 200, 200))
        screen.blit(text, (x, y - 8))


def draw_piece_at(screen, center, color, typ, pieces):
    img = get_piece_image(pieces, color, typ)
    rect = img.get_rect(center=center)
    screen.blit(img, rect)


def draw_pieces(screen, position, pieces, dragging):
    for (c, r), (color, typ) in position.items():
        if dragging is not None and (c, r) == dragging:
            continue
        x = MARGIN + c * CELL
        y = MARGIN + (BOARD_SIZE - 1 - r) * CELL
        draw_piece_at(screen, (x + CELL // 2, y + CELL // 2), color, typ, pieces)


def draw_highlights(screen, selected, moves, position, en_passant_moves, double_moves):
    if selected is None:
        return
    c, r = selected
    x = MARGIN + c * CELL
    y = MARGIN + (BOARD_SIZE - 1 - r) * CELL
    pygame.draw.rect(screen, SELECTED, (x, y, CELL, CELL), 4)
    for (mc, mr) in moves:
        mx = MARGIN + mc * CELL
        my = MARGIN + (BOARD_SIZE - 1 - mr) * CELL
        center = (mx + CELL // 2, my + CELL // 2)
        if (mc, mr) in double_moves:
            pygame.draw.circle(screen, DOUBLE_DOT, center, CELL // 2 - 10, 4)
        elif (mc, mr) in en_passant_moves:
            pygame.draw.circle(screen, EN_PASSANT_RING, center, CELL // 2 - 10, 4)
        elif (mc, mr) in position:
            pygame.draw.circle(screen, CAPTURE_RING, center, CELL // 2 - 10, 4)
        else:
            pygame.draw.circle(screen, MOVE_DOT, center, max(4, CELL // 8))


def draw_checks(screen, position, current_player):
    enemy = 'b' if current_player == 'w' else 'w'
    for (c, r), (pc, pt) in position.items():
        if pt == 'K' and pc == current_player:
            if is_square_attacked(position, c, r, enemy):
                x = MARGIN + c * CELL
                y = MARGIN + (BOARD_SIZE - 1 - r) * CELL
                pygame.draw.rect(screen, CHECK_COLOR, (x, y, CELL, CELL), 6)


def draw_dragged_piece(screen, position, dragging, drag_pos, pieces):
    if dragging is None or drag_pos is None:
        return
    if dragging not in position:
        return
    color, typ = position[dragging]
    draw_piece_at(screen, drag_pos, color, typ, pieces)


def draw_turn_indicator(screen, font, current_player):
    if current_player is None:
        return
    text = font.render(f"Ход: {PLAYER_LABELS[current_player]}", True, (255, 255, 255))
    screen.blit(text, (MARGIN, 10))


def draw_win_message(screen, big_font, winner):
    msg = f"Мат! Победа {PLAYER_LABELS[winner]}!"
    text = big_font.render(msg, True, WIN_COLOR)
    rect = text.get_rect(center=(WINDOW_W // 2, MARGIN + BOARD_SIZE * CELL // 2))
    bg = pygame.Surface((rect.width + 40, rect.height + 30), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 200))
    screen.blit(bg, (rect.x - 20, rect.y - 15))
    screen.blit(text, rect)


def draw_draw_message(screen, big_font):
    text = big_font.render("НИЧЬЯ", True, (200, 200, 255))
    rect = text.get_rect(center=(WINDOW_W // 2, MARGIN + BOARD_SIZE * CELL // 2))
    bg = pygame.Surface((rect.width + 40, rect.height + 30), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 200))
    screen.blit(bg, (rect.x - 20, rect.y - 15))
    screen.blit(text, rect)


def get_promotion_buttons(promotion_pending):
    if promotion_pending is None:
        return {}
    c, r, color = promotion_pending
    board_cx = MARGIN + BOARD_SIZE * CELL // 2
    board_cy = MARGIN + BOARD_SIZE * CELL // 2
    total_w = 4 * CELL + 3 * 10
    start_x = board_cx - total_w // 2
    y = board_cy - CELL // 2
    buttons = {}
    for i, typ in enumerate(PROMOTION_CHOICES):
        x = start_x + i * (CELL + 10)
        buttons[typ] = pygame.Rect(x, y, CELL, CELL)
    return buttons


def draw_promotion_window(screen, pieces, promotion_pending, font):
    if promotion_pending is None:
        return
    c, r, color = promotion_pending
    buttons = get_promotion_buttons(promotion_pending)
    if buttons:
        min_x = min(btn.x for btn in buttons.values())
        max_x = max(btn.x + btn.width for btn in buttons.values())
        min_y = min(btn.y for btn in buttons.values())
        max_y = max(btn.y + btn.height for btn in buttons.values())
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        padding = 20
        bg_rect = pygame.Rect(min_x - padding, min_y - padding - 40,
                              (max_x - min_x) + 2 * padding,
                              (max_y - min_y) + 2 * padding + 40)
        pygame.draw.rect(screen, (40, 40, 60), bg_rect)
        pygame.draw.rect(screen, (200, 200, 255), bg_rect, 3)
        title = font.render(f"Превращение: {PLAYER_LABELS[color]}", True, (255, 255, 255))
        title_rect = title.get_rect(center=(bg_rect.centerx, bg_rect.y + 20))
        screen.blit(title, title_rect)
        for typ, rect in buttons.items():
            pygame.draw.rect(screen, (200, 200, 200), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 3)
            img = get_piece_image(pieces, color, typ)
            screen.blit(img, img.get_rect(center=rect.center))
            label = {'Q': 'Ферзь', 'R': 'Ладья', 'B': 'Слон', 'N': 'Конь'}[typ]
            label_surf = font.render(label, True, (0, 0, 0))
            screen.blit(label_surf, label_surf.get_rect(
                center=(rect.centerx, rect.bottom + 15)))


def make_buttons():
    btn_w = 170
    btn_h = 36
    gap = 10
    back_w = 120  # Ширина кнопки "Назад"

    # Общая ширина: Back + 4 кнопки + отступы
    total_w = back_w + 4 * btn_w + 4 * gap
    start_x = (WINDOW_W - total_w) // 2
    y_row = MARGIN + BOARD_SIZE * CELL + 30

    back_btn = pygame.Rect(start_x, y_row, back_w, btn_h)
    surrender_btns = {}
    draw_btns = {}

    offset = back_w + gap
    for i, player in enumerate(TURN_ORDER):
        x = start_x + offset + i * (btn_w + gap)
        surrender_btns[player] = pygame.Rect(x, y_row, btn_w, btn_h)
        draw_btns[player] = pygame.Rect(x + 2 * (btn_w + gap), y_row, btn_w, btn_h)

    return back_btn, surrender_btns, draw_btns


def draw_buttons(screen, font, back_btn, surrender_btns, draw_btns,
                 vote_draw, current_player, game_over, history):
    # --- Кнопка "Назад" ---
    can_undo = len(history) > 0 and not game_over
    back_color = (120, 120, 200) if can_undo else (60, 60, 60)
    pygame.draw.rect(screen, back_color, back_btn)
    pygame.draw.rect(screen, (0, 0, 0), back_btn, 2)
    back_text = font.render("← Назад", True,
                            (255, 255, 255) if can_undo else (150, 150, 150))
    screen.blit(back_text, back_text.get_rect(center=back_btn.center))

    # --- Кнопки "Сдаться" ---
    for player in TURN_ORDER:
        rect = surrender_btns[player]
        color = PLAYER_COLORS[player] if player == current_player else (60, 60, 60)
        text_color = (0, 0, 0) if player == current_player else (220, 220, 220)
        label = f"Сдаться: {PLAYER_LABELS[player]}"
        if not game_over:
            pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        text = font.render(label, True, text_color)
        screen.blit(text, text.get_rect(center=rect.center))

    # --- Кнопки "Ничья" ---
    for player in TURN_ORDER:
        rect = draw_btns[player]
        if vote_draw[player]:
            color = (150, 150, 255); text_color = (0, 0, 0)
        else:
            color = (60, 60, 100); text_color = (220, 220, 220)
        label = f"Ничья: {PLAYER_LABELS[player]}"
        if not game_over:
            pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        text = font.render(label, True, text_color)
        screen.blit(text, text.get_rect(center=rect.center))


def undo_move(history, position, moved_pawns, en_passant_move, en_passant_moves,
              winner, is_draw, current_player, promotion_pending,
              dragging, drag_pos, drag_moves, drag_double_moves):
    """Откатывает один ход назад из истории."""
    if not history:
        return (position, moved_pawns, en_passant_move, en_passant_moves,
                winner, is_draw, current_player, promotion_pending,
                dragging, drag_pos, drag_moves, drag_double_moves)

    (old_pos, from_sq, to_sq, captured,
     moved_before, ep_move_before, ep_moves_before,
     winner_before, draw_before, current_before) = history.pop()

    position = dict(old_pos)
    moved_pawns = set(moved_before)
    en_passant_move = ep_move_before
    en_passant_moves = dict(ep_moves_before)
    winner = winner_before
    is_draw = draw_before
    current_player = current_before
    promotion_pending = None
    dragging = None
    drag_pos = None
    drag_moves = []
    drag_double_moves = {}

    return (position, moved_pawns, en_passant_move, en_passant_moves,
            winner, is_draw, current_player, promotion_pending,
            dragging, drag_pos, drag_moves, drag_double_moves)


def main():
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Командные шахматы 2 на 2")
    font = pygame.font.SysFont("Arial", max(14, CELL // 5))
    turn_font = pygame.font.SysFont("Arial", max(14, CELL // 6), bold=True)
    big_font = pygame.font.SysFont("Arial", max(24, CELL // 2), bold=True)
    btn_font = pygame.font.SysFont("Arial", 14)
    promo_font = pygame.font.SysFont("Arial", max(16, CELL // 4), bold=True)

    pieces = load_pieces()
    position = initial_position()
    history = []
    moved_pawns = set()
    en_passant_move = None
    en_passant_moves = {}

    dragging = None
    drag_pos = None
    drag_moves = []
    drag_double_moves = {}

    vote_draw = {'w': False, 'b': False}
    winner = None
    is_draw = False
    current_player = 'w'
    promotion_pending = None

    back_btn, surrender_btns, draw_btns = make_buttons()

    running = True
    while running:
        game_over = (winner is not None) or is_draw

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if promotion_pending is not None:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = get_promotion_buttons(promotion_pending)
                    for typ, rect in buttons.items():
                        if rect.collidepoint(event.pos):
                            c, r, color = promotion_pending
                            position[(c, r)] = (color, typ)
                            promotion_pending = None
                            current_player = 'b' if current_player == 'w' else 'w'
                            en_passant_move = None
                            en_passant_moves = {}
                            if is_checkmate(position, current_player, moved_pawns, en_passant_moves):
                                winner = 'w' if current_player == 'b' else 'b'
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
                    (position, moved_pawns, en_passant_move, en_passant_moves,
                     winner, is_draw, current_player, promotion_pending,
                     dragging, drag_pos, drag_moves, drag_double_moves) = undo_move(
                        history, position, moved_pawns, en_passant_move, en_passant_moves,
                        winner, is_draw, current_player, promotion_pending,
                        dragging, drag_pos, drag_moves, drag_double_moves)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue
                mx, my = event.pos
                if game_over:
                    continue

                # --- Кнопка "Назад" ---
                if back_btn.collidepoint(mx, my) and history:
                    (position, moved_pawns, en_passant_move, en_passant_moves,
                     winner, is_draw, current_player, promotion_pending,
                     dragging, drag_pos, drag_moves, drag_double_moves) = undo_move(
                        history, position, moved_pawns, en_passant_move, en_passant_moves,
                        winner, is_draw, current_player, promotion_pending,
                        dragging, drag_pos, drag_moves, drag_double_moves)
                    continue

                clicked_surrender = False
                for player, rect in surrender_btns.items():
                    if rect.collidepoint(mx, my):
                        old_pos = dict(position)
                        moved_before = set(moved_pawns)
                        winner_before = winner
                        draw_before = is_draw
                        current_before = current_player
                        winner = 'w' if player == 'b' else 'b'
                        clicked_surrender = True
                        history.append((old_pos, None, None, None,
                                        moved_before, en_passant_move,
                                        dict(en_passant_moves),
                                        winner_before, draw_before, current_before))
                        break
                if clicked_surrender:
                    continue

                clicked_draw = False
                for player, rect in draw_btns.items():
                    if rect.collidepoint(mx, my):
                        old_pos = dict(position)
                        moved_before = set(moved_pawns)
                        winner_before = winner
                        draw_before = is_draw
                        current_before = current_player
                        vote_draw[player] = not vote_draw[player]
                        clicked_draw = True
                        if all(vote_draw.values()):
                            is_draw = True
                        history.append((old_pos, None, None, None,
                                        moved_before, en_passant_move,
                                        dict(en_passant_moves),
                                        winner_before, draw_before, current_before))
                        break
                if clicked_draw:
                    continue

                c = (mx - MARGIN) // CELL
                r = BOARD_SIZE - 1 - (my - MARGIN) // CELL
                if not in_bounds(c, r):
                    continue
                if (c, r) in position:
                    piece_color, piece_type = position[(c, r)]
                    if piece_color == current_player:
                        dragging = (c, r)
                        drag_pos = (mx, my)
                        drag_moves = filter_legal_moves(position, c, r, piece_color,
                                                        moved_pawns, en_passant_moves)
                        drag_double_moves = {}
                        if piece_type == 'R2':
                            first_moves, double_moves = compute_double_moves_cheetah(
                                position, c, r, piece_color, moved_pawns, en_passant_moves)
                            drag_double_moves = double_moves
                            for fm in double_moves.keys():
                                if fm not in drag_moves:
                                    drag_moves.append(fm)

            elif event.type == pygame.MOUSEMOTION:
                if dragging is not None:
                    drag_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button != 1 or dragging is None:
                    continue
                mx, my = event.pos
                c = (mx - MARGIN) // CELL
                r = BOARD_SIZE - 1 - (my - MARGIN) // CELL
                if in_bounds(c, r) and (c, r) in drag_moves:
                    old_pos = dict(position)
                    moved_before = set(moved_pawns)
                    ep_move_before = en_passant_move
                    ep_moves_before = dict(en_passant_moves)
                    winner_before = winner
                    draw_before = is_draw
                    current_before = current_player

                    is_en_passant = (c, r) in en_passant_moves
                    enemy_pos = en_passant_moves.get((c, r))
                    if is_en_passant and enemy_pos is not None:
                        if enemy_pos in position:
                            del position[enemy_pos]

                    is_double_move = (c, r) in drag_double_moves

                    if is_double_move:
                        mid_c, mid_r = drag_double_moves[(c, r)]
                        moved_piece = position.pop(dragging)
                        position[(c, r)] = moved_piece
                    else:
                        captured = position.get((c, r), None)
                        moved_piece = position.pop(dragging)
                        position[(c, r)] = moved_piece

                    en_passant_move = None
                    if moved_piece[1] == 'P':
                        dc, dr = PAWN_FORWARD[current_player]
                        distance = abs(r - dragging[1]) if dr != 0 else abs(c - dragging[0])
                        if distance >= 2:
                            en_passant_move = (dragging[0], dragging[1],
                                               c, r, current_player)
                        moved_pawns.add((c, r))

                    en_passant_moves = compute_en_passant(position, en_passant_move)

                    is_promo = (moved_piece[1] == 'P'
                                and is_promotion_square_for(current_player, c, r))
                    if is_promo:
                        promotion_pending = (c, r, current_player)
                    else:
                        current_player = 'b' if current_player == 'w' else 'w'
                        if is_checkmate(position, current_player, moved_pawns, en_passant_moves):
                            winner = 'w' if current_player == 'b' else 'b'

                    history.append((old_pos, dragging, (c, r), None,
                                    moved_before, ep_move_before,
                                    ep_moves_before, winner_before, draw_before,
                                    current_before))

                dragging = None
                drag_pos = None
                drag_moves = []
                drag_double_moves = {}

        # Отрисовка
        screen.fill((30, 30, 30))
        draw_board(screen, font)
        draw_checks(screen, position, current_player)
        if dragging is not None:
            draw_highlights(screen, dragging, drag_moves, position,
                            en_passant_moves, drag_double_moves)
        draw_pieces(screen, position, pieces, dragging)
        draw_dragged_piece(screen, position, dragging, drag_pos, pieces)
        if promotion_pending is None:
            draw_turn_indicator(screen, turn_font, current_player)
        draw_buttons(screen, btn_font, back_btn, surrender_btns, draw_btns,
                     vote_draw, current_player, game_over, history)
        if winner is not None:
            draw_win_message(screen, big_font, winner)
        elif is_draw:
            draw_draw_message(screen, big_font)
        elif promotion_pending is not None:
            draw_promotion_window(screen, pieces, promotion_pending, promo_font)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
