from itertools import product
import numpy as np
import string

import pygame
from pygame import Surface

from src.ai import AI, PositionEvaluation
from src.boardstate import BoardState


def draw_board(screen: Surface, pos_x: int, pos_y: int, elem_size: int, board: BoardState):
    dark = (0, 0, 0)
    white = (200, 200, 200)
    if board.current_player == -1:
        board = board.inverted()
    for y, x in product(range(8), range(8)):
        color = white if (x + y) % 2 == 0 else dark
        position = pos_x + x * elem_size, pos_y + y * elem_size, elem_size, elem_size
        pygame.draw.rect(screen, color, position)

        figure = board.board[y, x]

        if figure == 0:
            continue

        if figure > 0:
            figure_color = 255, 255, 255
        else:
            figure_color = 100, 100, 100
        r = elem_size // 2 - 10

        pygame.draw.circle(screen, figure_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)
        if abs(figure) == 2:
            r = 5
            negative_color = [255 - e for e in figure_color]
            pygame.draw.circle(screen, negative_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)


def game_loop(screen: Surface, board: BoardState, ai: AI):
    grid_size = screen.get_size()[0] // 8
    list_state = [str(board.board)]
    automatic = False
    while True:
        if board.is_game_finished:
            break
        if automatic:
            board = ai.next_move(board)
            list_state.append(str(board.board))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if automatic:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click_position = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                new_x, new_y = [p // grid_size for p in event.pos]
                old_x, old_y = [p // grid_size for p in mouse_click_position]
                new_board = board.do_move(old_x, old_y, new_x, new_y)
                if new_board is not None:
                    board = new_board
                    list_state.append(board)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                x, y = [p // grid_size for p in event.pos]
                board.board[y, x] = (board.board[y, x] + 1 + 2) % 5 - 2  # change figure
                board.update()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = board.inverted()
                    board.update()

                if event.key == pygame.K_s and  board.choosed == None and not board.turn_ended:
                    board.save()

                if event.key == pygame.K_l:
                    field = np.zeros(shape=(8, 8), dtype=np.int8)
                    with open("save.txt", "r") as f:
                        for i in range(0, 8):
                            lst = f.readline().split()
                            for j in range(0, 8):
                                field[i][j] = lst[j]
                        board = BoardState(field, 1)
                if event.key == pygame.K_a:
                    automatic = True

                if event.key == pygame.K_SPACE:
                    new_board = ai.next_move(board.inverted())
                    list_state.append(str(board.board))
                    if new_board is not None:
                        while (new_board.current_player == -1):
                            new_board = ai.next_move(new_board)
                            list_state.append(str(board.board))
                        board = new_board
        if list_state.count(str(board.board)) >= 3:
            board.draw = True
        draw_board(screen, 0, 0, grid_size, board)
        pygame.display.flip()
        pygame.time.delay(100)
    pygame.font.SysFont('arial', 36)
    screen.fill((255, 255, 255))
    f1 = pygame.font.Font(None, 30)
    text = ''
    if board.is_win(1):
        text = 'Поздравляю с победой!'
    if board.is_win(-1):
        text = 'Сочувствую твоей неудаче...'
    if board.is_draw():
        text = 'Ничья'
    text1 = f1.render(text, 1, (0, 0, 0))
    screen.blit(text1, (100, 50))
    pygame.display.update()
    pygame.time.delay(10000)


pygame.init()

screen: Surface = pygame.display.set_mode([512, 512])
ai = AI(PositionEvaluation(), search_depth=4)

game_loop(screen, BoardState.initial_state(), ai)

pygame.quit()
