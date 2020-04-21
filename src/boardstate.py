import numpy as np
import string
from typing import Optional, List

class position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class BoardState:
    def __init__(self, board: np.ndarray, current_player: int = 1):
        self.board: np.ndarray = board
        self.current_player: int = current_player
        self.choosed = None
        self.turn_ended = False
        self.draw = False
        self.can_eat = self.has_eating_move()

    def inverted(self) -> 'BoardState':
        return BoardState(board=self.board[::-1, ::-1] * -1, current_player=self.current_player * -1)

    def copy(self) -> 'BoardState':
        newstate = BoardState(self.board.copy(), self.current_player)
        newstate.turn_ended = False
        newstate.update()
        return newstate

    def can_basic_move(self, from_x, from_y, to_x, to_y) -> bool:
        if self.turn_ended:
            return False
        if from_x == to_x and from_y == to_y:
            return False
        if (to_x + to_y) % 2 == 0:
            return False
        if self.board[from_y, from_x] <= 0:
            return False
        if self.board[to_y, to_x] != 0:
            return False
        if to_x + to_y != from_x + from_y and to_x - to_y != from_x - from_y:
            return False
        if self.board[from_y, from_x] == 1:
            if abs(from_x - to_x) > 2:
                return False
            if abs(from_x - to_x) == 2 and self.board[(to_y + from_y) // 2, (to_x + from_x) // 2] >= 0:
                return False
            if from_y - to_y == -1:
                return False
        if self.board[from_y, from_x] == 2:
            dx = (to_x - from_x > 0) * 2 - 1
            dy = (to_y - from_y > 0) * 2 - 1
            temp_x = from_x + dx
            temp_y = from_y + dy
            while temp_x != to_x and to_y != temp_y:
                if self.board[temp_y, temp_x] > 0:
                    return False
                temp_x = temp_x + dx
                temp_y = temp_y + dy
        if self.choosed != None and self.choosed.x != from_x and self.choosed.y != from_y:
            return False
        return True

    def is_eating_move(self, from_x, from_y, to_x, to_y):
        dx = (to_x - from_x > 0) * 2 - 1
        dy = (to_y - from_y > 0) * 2 - 1
        temp_x = from_x + dx
        temp_y = from_y + dy
        while temp_x != to_x and to_y != temp_y:
            if self.board[temp_y, temp_x] < 0:
                return True
            temp_x = temp_x + dx
            temp_y = temp_y + dy
        return False

    def update(self):
        self.can_eat = self.has_eating_move()

    def do_move(self, from_x, from_y, to_x, to_y) -> Optional['BoardState']:
        """
        :return: new BoardState or None for invalid move
        """
        if not self.can_basic_move(from_x, from_y, to_x, to_y) or (self.can_eat and not self.is_eating_move(from_x, from_y, to_x, to_y)):
            return None
        # todo more validation here
        Eat = self.is_eating_move(from_x, from_y, to_x, to_y)
        result = self.copy()
        result.board[to_y, to_x] = result.board[from_y, from_x]
        dx = (to_x - from_x > 0) * 2 - 1
        dy = (to_y - from_y > 0) * 2 - 1
        while from_x != to_x and to_y != from_y:
            result.board[from_y, from_x] = 0
            from_x = from_x + dx
            from_y = from_y + dy
        if to_y == 0:
            result.board[to_y, to_x] = 2
        result.choosed = position(to_x, to_y)
        if Eat:
            result.update()
        if not (Eat and result.can_eat):
            result.turn_ended = True
        return result

    def do_turn(self, from_x, from_y, to_x, to_y) -> Optional['BoardState']:
        new_board = self.do_move(from_x, from_y, to_x, to_y)
        if new_board == None:
            return None
        if new_board.turn_ended:
            new_board = new_board.inverted()
        return new_board

    def save(self, file_name = "save.txt"):
        f = open(file_name, 'w')  # открытие в режиме записи
        for i in range(0, 8):
            out = ''
            for j in range(0, 8):
                out = out + str(self.board[i, j]) + ' '
            f.write(out + '\n')
        f.close()

    def has_eating_move(self) -> bool:
        for from_y in range(0, 8):
            for from_x in range(0, 8):
                if self.board[from_y, from_x] > 0 and (self.choosed == None or (self.choosed.x == from_x and self.choosed.y == from_y)):
                    if self.board[from_y, from_x] == 1:
                        may_be = []
                        if from_y > 1:
                            may_be.append(from_y - 2)
                        if from_y < 6:
                            may_be.append(from_y + 2)
                    else:
                        may_be = range(0, 8)
                    for to_y in may_be:
                        for to_x in [from_x + from_y - to_y, from_x - from_y + to_y]:
                            if 0 <= to_x < 8:
                                if self.can_basic_move(from_x, from_y, to_x, to_y) and self.is_eating_move(from_x, from_y, to_x, to_y):
                                    return True
        return False

    def get_possible_moves(self) -> List['BoardState']:
        ans = []
        for from_y in range(0, 8):
            for from_x in range(0, 8):
                if self.board[from_y, from_x] > 0 and (self.choosed == None or (self.choosed.x == from_x and self.choosed.y == from_y)):
                    for to_y in range(0, 8):
                        for to_x in [from_x + from_y - to_y, from_x - from_y + to_y]:
                            if 0 <= to_x < 8:
                                new_board = self.do_turn(from_x, from_y, to_x, to_y)
                                if new_board != None:
                                    ans.append(new_board)
        return ans # todo

    def count_obj(self, player, type):
        cnt = 0
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i, j] * self.current_player == type * player:
                    cnt += 1
        return cnt

    def is_win(self, player):
        if self.count_obj(-player, 1) + self.count_obj(-player, 2) == 0:
            return True
        if player == -self.current_player and not self.turn_ended and len(self.get_possible_moves()) == 0:
            return True
        return False

    def is_draw(self):
        return self.draw

    @property
    def is_game_finished(self) -> bool:
        if self.is_win(1):
            return True
        if self.is_win(-1):
            return True
        if self.is_draw():
            return True
        return False
        ... # todo

    @property
    def get_winner(self) -> Optional[int]:
        if self.is_win(1):
            return 1
        if self.is_win(-1):
            return -1
        if self.is_draw():
            return 0
        return None

    @staticmethod
    def initial_state() -> 'BoardState':
        board = np.zeros(shape=(8, 8), dtype=np.int8)
        for i in range(0, 8):
            for j in range(0, 8):
                if (i + j) % 2 == 1:
                    if i <= 2:
                        board[i][j] = -1
                    if i >= 5:
                        board[i][j] = 1

        return BoardState(board, 1)
