from typing import Optional

from .boardstate import BoardState


class PositionEvaluation:
    def __call__(self, board: BoardState) -> float:
        if board.is_draw():
            return 0
        a = float(0)
        for i in range(0, 8):
            for j in range(0, 8):
                a += board.board[i, j] ** 3
                if board.board[i, j] == 1:
                    a += (7 - i) / 10
                if board.board[i, j] == -1:
                    a -= i / 10
        #todo
        return a


class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth: int = search_depth
        self.cnt = 0

    def position_analis(self, board: BoardState, deep) -> float:
        if deep == 0:
            return self.position_evaluation(board)
        moves = board.get_possible_moves()
        self.cnt = self.cnt + 1
        if len(moves) == 0:
            return 0
        a = max(self.position_analis(b, deep - 1) * b.current_player * board.current_player for b in moves)
        return a

    def next_move(self, board: BoardState) -> Optional[BoardState]:
        moves = board.get_possible_moves()
        self.cnt = 0
        if len(moves) == 0:
            return None
        return max(moves, key=lambda b: self.position_analis(b, self.depth - 1) * b.current_player * board.current_player)

