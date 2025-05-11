import os
import time
import random
import sys

class NineMensMorris:
    def __init__(self):
        self.board = [0] * 24
        self.phase = 1
        self.player_pieces_to_place = 9
        self.ai_pieces_to_place = 9
        self.player_pieces_on_board = 0
        self.ai_pieces_on_board = 0
        self.last_player_move = None
        self.last_ai_move = None
        self.winner = None
        self.player_turn = True

        self.coordinates = {
            0: "A7", 1: "D7", 2: "G7", 3: "B6", 4: "D6", 5: "F6",
            6: "C5", 7: "D5", 8: "E5", 9: "A4", 10: "B4", 11: "C4",
            12: "E4", 13: "F4", 14: "G4", 15: "C3", 16: "D3", 17: "E3",
            18: "B2", 19: "D2", 20: "F2", 21: "A1", 22: "D1", 23: "G1"
        }
        self.position_map = {v: k for k, v in self.coordinates.items()}
        self.adjacent_positions = [
            [1, 9], [0, 2, 4], [1, 14], [4, 10], [1, 3, 5, 7], [4, 13],
            [7, 11], [4, 6, 8], [7, 12], [0, 10, 21], [3, 9, 11, 18],
            [6, 10, 15], [8, 13, 17], [5, 12, 14, 20], [2, 13, 23],
            [11, 16], [15, 17, 19], [12, 16], [10, 19], [16, 18, 20, 22],
            [13, 19], [9, 22], [19, 21, 23], [14, 22]
        ]
        self.mills = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14],
            [15, 16, 17], [18, 19, 20], [21, 22, 23], [0, 9, 21],
            [3, 10, 18], [6, 11, 15], [1, 4, 7], [16, 19, 22],
            [8, 12, 17], [5, 13, 20], [2, 14, 23]
        ]

        self.player_bomb_available = True
        self.ai_bomb_available = True
        self.bombs_on_board = []
        self.next_bomb_id = 0
        self.BOMB_INITIAL_TIMER = 3
        self.player_undos_left = 3
        self._undo_stack = []

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_piece_symbol(self, value, pos=None):
        # If pos is provided and there is a bomb at this position, color it red
        if pos is not None and any(bomb['position'] == pos for bomb in self.bombs_on_board):
            # ANSI escape code for red
            if value == 1:
                return '\033[91mO\033[0m'
            elif value == 2:
                return '\033[91mX\033[0m'
        if value == 0: return "·"
        elif value == 1: return "O"
        else: return "X"

    def format_move(self, move_details):
        if move_details is None: return "None"
        try:
            to_pos, from_pos, removed_pos = move_details
        except (ValueError, TypeError):
             return f"Error: {move_details}"

        to_coord = self.coordinates.get(to_pos, f"?({to_pos})")
        action = ""
        removal_info = ""

        if from_pos == -1: action = f"Placed at {to_coord}"
        elif from_pos == -2: action = f"Placed Time Bomb at {to_coord}"
        elif from_pos is not None:
            from_coord = self.coordinates.get(from_pos, f"?({from_pos})")
            action = f"Moved from {from_coord} to {to_coord}"
        else: action = f"Error move data (to:{to_coord})"

        if removed_pos is not None:
            removed_coord = self.coordinates.get(removed_pos, f"?({removed_pos})")
            removal_info = f", removed piece at {removed_coord}"
        return action + removal_info

    def display_board(self):
        self.clear_screen()
        phase_desc = "Phase 1: Placing"
        player_done_placing = self.player_pieces_to_place == 0
        ai_done_placing = self.ai_pieces_to_place == 0
        if player_done_placing and ai_done_placing:
            is_player_flying = self.player_pieces_on_board <= 3
            is_ai_flying = self.ai_pieces_on_board <= 3
            current_phase = 3 if is_player_flying or is_ai_flying else 2
            if current_phase != self.phase: self.phase = current_phase
            phase_desc = f"Phase {self.phase}: {'Flying' if self.phase == 3 else 'Moving'}"
        else:
             if self.phase != 1: self.phase = 1
             phase_desc = "Phase 1: Placing"

        print(f"\n  Nine Men's Morris - {phase_desc}")
        print(f"  Player: O ({self.player_pieces_on_board} on board, {self.player_pieces_to_place} to place), Bomb Available: {'Yes' if self.player_bomb_available else 'No'}")
        print(f"  AI: X ({self.ai_pieces_on_board} on board, {self.ai_pieces_to_place} to place), Bomb Available: {'Yes' if self.ai_bomb_available else 'No'}")
        print("\n  Game Board (coordinate system A1-G7):\n")
        
        # Use get_piece_symbol with bomb highlighting
        p = [self.get_piece_symbol(self.board[i], i) for i in range(24)]

        print(f"    A   B   C   D   E   F   G")
        print(f"7   {p[0]}-----------{p[1]}-----------{p[2]}")
        print(f"    |           |           |")
        print(f"6   |   {p[3]}-------{p[4]}-------{p[5]}   |")
        print(f"    |   |       |       |   |")
        print(f"5   |   |   {p[6]}---{p[7]}---{p[8]}   |   |")
        print(f"    |   |   |       |   |   |")
        print(f"4   {p[9]}---{p[10]}---{p[11]}       {p[12]}---{p[13]}---{p[14]}")
        print(f"    |   |   |       |   |   |")
        print(f"3   |   |   {p[15]}---{p[16]}---{p[17]}   |   |")
        print(f"    |   |       |       |   |")
        print(f"2   |   {p[18]}-------{p[19]}-------{p[20]}   |")
        print(f"    |           |           |")
        print(f"1   {p[21]}-----------{p[22]}-----------{p[23]}")
        print(f"    A   B   C   D   E   F   G")
        print("\n  Last moves:")
        player_move_str = self.format_move(self.last_player_move)
        ai_move_str = self.format_move(self.last_ai_move)
        print(f"  Player: {player_move_str}")
        print(f"  AI: {ai_move_str}")

        print("\n  Active Time Bombs:")
        if not self.bombs_on_board:
            print("    None")
        else:
            for bomb in self.bombs_on_board:
                owner = "Player (O)" if bomb['player_id'] == 1 else "AI (X)"
                pos_coord = self.coordinates.get(bomb['position'], f"?({bomb['position']})")
                print(f"    ID {bomb['id']}: {owner} at {pos_coord}, Detonates in {bomb['timer']} of their turn(s).")

    def is_valid_place(self, position):
        return 0 <= position <= 23 and self.board[position] == 0

    def is_valid_move(self, from_pos, to_pos, player):
        if not (0 <= from_pos <= 23 and 0 <= to_pos <= 23): return False
        if self.board[from_pos] != player or self.board[to_pos] != 0: return False
        pieces_on_board = self.player_pieces_on_board if player == 1 else self.ai_pieces_on_board
        pieces_to_place = self.player_pieces_to_place if player == 1 else self.ai_pieces_to_place
        can_fly = (pieces_on_board <= 3) and (pieces_to_place == 0)
        if pieces_to_place > 0: return False
        if can_fly: return True
        else: return to_pos in self.adjacent_positions[from_pos]

    def forms_mill(self, position, player):
        if not (0 <= position <= 23) or self.board[position] != player: return False
        for mill in self.mills:
            if position in mill:
                if all(self.board[pos] == player for pos in mill):
                    return True
        return False

    def is_in_mill(self, position, player):
        if not (0 <= position <= 23) or self.board[position] != player: return False
        for mill in self.mills:
            if position in mill:
                if all(self.board[pos] == player for pos in mill):
                    return True
        return False

    def is_valid_removal(self, position, player_making_removal):
        opponent = 3 - player_making_removal
        if not (0 <= position <= 23): return False
        if self.board[position] != opponent: return False
        opponent_in_mill = self.is_in_mill(position, opponent)
        if not opponent_in_mill: return True
        all_opponent_pieces_in_mills = True
        for pos in range(24):
            if self.board[pos] == opponent and not self.is_in_mill(pos, opponent):
                all_opponent_pieces_in_mills = False
                break
        return all_opponent_pieces_in_mills

    def get_valid_moves(self, player):
        valid_moves = []
        pieces_to_place = self.player_pieces_to_place if player == 1 else self.ai_pieces_to_place
        pieces_on_board = self.player_pieces_on_board if player == 1 else self.ai_pieces_on_board
        if pieces_to_place > 0:
            return [(pos, -1) for pos in range(24) if self.board[pos] == 0]
        can_fly = (pieces_on_board <= 3)
        player_piece_indices = [i for i, piece in enumerate(self.board) if piece == player]
        empty_indices = [i for i, piece in enumerate(self.board) if piece == 0]
        if can_fly:
            for from_pos in player_piece_indices:
                for to_pos in empty_indices:
                    valid_moves.append((to_pos, from_pos))
        else:
            for from_pos in player_piece_indices:
                for adj_pos in self.adjacent_positions[from_pos]:
                    if adj_pos in empty_indices:
                        valid_moves.append((adj_pos, from_pos))
        return valid_moves

    def make_move(self, move, player):
        to_pos, from_pos = move
        mill_formed = False
        move_details = (to_pos, from_pos, None)
        if from_pos == -1:
            if self.is_valid_place(to_pos):
                self.board[to_pos] = player
                if player == 1:
                    self.player_pieces_to_place -= 1; self.player_pieces_on_board += 1
                    self.last_player_move = move_details
                else:
                    self.ai_pieces_to_place -= 1; self.ai_pieces_on_board += 1
                    self.last_ai_move = move_details
                mill_formed = self.forms_mill(to_pos, player)
                return mill_formed
            else: return False
        else:
            if self.is_valid_move(from_pos, to_pos, player):
                self.board[from_pos] = 0
                self.board[to_pos] = player
                if player == 1: self.last_player_move = move_details
                else: self.last_ai_move = move_details
                for bomb in self.bombs_on_board:
                    if bomb['position'] == from_pos and bomb['player_id'] == player:
                        bomb['position'] = to_pos
                        break
                mill_formed = self.forms_mill(to_pos, player)
                return mill_formed
            else: return False

    def perform_removal(self, remove_pos, player_making_removal):
        opponent = 3 - player_making_removal
        if self.is_valid_removal(remove_pos, player_making_removal):
            # --- Fix: Remove bomb if present on removed piece ---
            for bomb in list(self.bombs_on_board):
                if bomb['position'] == remove_pos:
                    self.bombs_on_board.remove(bomb)
                    owner_str = "Player's" if bomb['player_id'] == 1 else "AI's"
                    print(f"{owner_str} Time Bomb (ID {bomb['id']}) at {self.coordinates.get(remove_pos)} was on a removed piece and has been disarmed.")
                    time.sleep(0.5)
                    break
            # --- END Fix ---
            self.board[remove_pos] = 0
            last_move_tuple = None
            if opponent == 1:
                self.player_pieces_on_board -= 1
                last_move_tuple = self.last_ai_move
            else:
                self.ai_pieces_on_board -= 1
                last_move_tuple = self.last_player_move
            if last_move_tuple:
                to_pos, from_pos, _ = last_move_tuple
                updated_move = (to_pos, from_pos, remove_pos)
                if player_making_removal == 1: self.last_player_move = updated_move
                else: self.last_ai_move = updated_move
            else:
                 print(f"Error: perform_removal({player_making_removal}) - last move not found.")
            return True
        else:
            return False

    def undo_move(self, move_details, player):
        if move_details is None: return
        to_pos, from_pos, removed_pos = move_details
        opponent = 3 - player
        if removed_pos is not None:
            if 0 <= removed_pos <= 23 and self.board[removed_pos] == 0:
                 self.board[removed_pos] = opponent
                 if opponent == 1: self.player_pieces_on_board += 1
                 else: self.ai_pieces_on_board += 1
        if from_pos == -1:
            if 0 <= to_pos <= 23 and self.board[to_pos] == player:
                self.board[to_pos] = 0
                if player == 1:
                    self.player_pieces_to_place += 1; self.player_pieces_on_board -= 1
                else:
                    self.ai_pieces_to_place += 1; self.ai_pieces_on_board -= 1
        elif from_pos is not None and from_pos != -2:
             if 0 <= to_pos <= 23 and self.board[to_pos] == player:
                  self.board[to_pos] = 0
                  if 0 <= from_pos <= 23 and self.board[from_pos] == 0:
                      self.board[from_pos] = player

    def evaluate_board(self):
        if self.is_game_over():
            if self.winner == "AI": return 10000
            if self.winner == "Player": return -10000
            return 0
        self.winner = None
        ai_pieces = self.ai_pieces_on_board
        player_pieces = self.player_pieces_on_board
        ai_done_placing = self.ai_pieces_to_place == 0
        player_done_placing = self.player_pieces_to_place == 0
        ai_can_fly = ai_done_placing and ai_pieces <= 3
        player_can_fly = player_done_placing and player_pieces <= 3
        is_flying_phase = ai_can_fly or player_can_fly
        piece_diff = ai_pieces - player_pieces
        pieces_to_place_diff = self.ai_pieces_to_place - self.player_pieces_to_place
        ai_mills_count = 0
        player_mills_count = 0
        ai_almost_mills = 0
        player_almost_mills = 0
        for mill in self.mills:
            counts = {0: 0, 1: 0, 2: 0}
            for pos in mill: counts[self.board[pos]] += 1
            if counts[2] == 3: ai_mills_count += 1
            elif counts[1] == 3: player_mills_count += 1
            elif counts[2] == 2 and counts[0] == 1: ai_almost_mills += 1
            elif counts[1] == 2 and counts[0] == 1: player_almost_mills += 1
        mill_diff = ai_mills_count - player_mills_count
        almost_mill_diff = ai_almost_mills - player_almost_mills
        ai_valid_moves = self.get_valid_moves(2)
        player_valid_moves = self.get_valid_moves(1)
        mobility_diff = len(ai_valid_moves) - len(player_valid_moves)
        ai_blocked = 1 if ai_done_placing and not ai_valid_moves else 0
        player_blocked = 1 if player_done_placing and not player_valid_moves else 0
        score = 0
        score += piece_diff * 200
        score += mill_diff * 300
        score += pieces_to_place_diff * 5
        if ai_done_placing or player_done_placing:
             score += almost_mill_diff * 50
             score += mobility_diff * 5
             score += player_blocked * 2000
             score -= ai_blocked * 4000
        if is_flying_phase:
            score += mill_diff * 100
            score += almost_mill_diff * 25
            if ai_can_fly and not player_can_fly: score += 100
            elif player_can_fly and not ai_can_fly: score -= 150
        if ai_done_placing and ai_pieces < 3: return -10000
        if player_done_placing and player_pieces < 3: return 10000
        if player_blocked: return 10000
        if ai_blocked: return -10000
        return score

    def alpha_beta_search(self, depth, alpha, beta, maximizing_player):
        if self.is_game_over():
            return self.evaluate_board(), None
        if depth == 0:
            return self.evaluate_board(), None
        current_player = 2 if maximizing_player else 1
        valid_moves = self.get_valid_moves(current_player)
        if not valid_moves:
            return self.evaluate_board(), None
        best_full_move_details = None
        ordered_moves = sorted(valid_moves, key=lambda move: self.move_creates_mill_heuristic(move, current_player), reverse=True)
        if maximizing_player:
            max_eval = float('-inf')
            for move in ordered_moves:
                mill_formed = self.make_move(move, current_player)
                current_basic_move_details = self.last_ai_move
                move_branch_eval = float('-inf')
                best_remove_for_this_move = None
                if mill_formed:
                    remove_options = [p for p in range(24) if self.is_valid_removal(p, current_player)]
                    if not remove_options:
                        eval_score, _ = self.alpha_beta_search(depth - 1, alpha, beta, False)
                        move_branch_eval = eval_score
                    else:
                        for remove_pos in remove_options:
                            opponent_val = 1; original_piece = self.board[remove_pos]
                            self.board[remove_pos] = 0; self.player_pieces_on_board -= 1
                            disarmed_bomb_during_search = None
                            for b_search in list(self.bombs_on_board):
                                if b_search['position'] == remove_pos:
                                    disarmed_bomb_during_search = b_search
                                    self.bombs_on_board.remove(b_search)
                                    break
                            eval_score, _ = self.alpha_beta_search(depth - 1, alpha, beta, False)
                            if disarmed_bomb_during_search:
                                self.bombs_on_board.append(disarmed_bomb_during_search)
                            self.board[remove_pos] = original_piece; self.player_pieces_on_board += 1
                            if eval_score > move_branch_eval:
                                move_branch_eval = eval_score; best_remove_for_this_move = remove_pos
                else:
                    eval_score, _ = self.alpha_beta_search(depth - 1, alpha, beta, False)
                    move_branch_eval = eval_score
                self.undo_move(current_basic_move_details, current_player)
                if move_branch_eval > max_eval:
                    max_eval = move_branch_eval; best_full_move_details = (move, best_remove_for_this_move)
                alpha = max(alpha, max_eval)
                if beta <= alpha: break
            return max_eval, best_full_move_details
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                mill_formed = self.make_move(move, current_player)
                current_basic_move_details = self.last_player_move
                move_branch_eval = float('inf')
                best_remove_for_this_move = None
                if mill_formed:
                    remove_options = [p for p in range(24) if self.is_valid_removal(p, current_player)]
                    if not remove_options:
                        eval_score, _ = self.alpha_beta_search(depth - 1, alpha, beta, True)
                        move_branch_eval = eval_score
                    else:
                        for remove_pos in remove_options:
                            opponent_val = 2; original_piece = self.board[remove_pos]
                            self.board[remove_pos] = 0; self.ai_pieces_on_board -= 1
                            disarmed_bomb_during_search = None
                            for b_search in list(self.bombs_on_board):
                                if b_search['position'] == remove_pos:
                                    disarmed_bomb_during_search = b_search
                                    self.bombs_on_board.remove(b_search)
                                    break
                            eval_score, _ = self.alpha_beta_search(depth - 1, alpha, beta, True)
                            if disarmed_bomb_during_search:
                                self.bombs_on_board.append(disarmed_bomb_during_search)
                            self.board[remove_pos] = original_piece; self.ai_pieces_on_board += 1
                            if eval_score < move_branch_eval:
                                move_branch_eval = eval_score; best_remove_for_this_move = remove_pos
                else:
                    eval_score, _ = self.alpha_beta_search(depth - 1, alpha, beta, True)
                    move_branch_eval = eval_score
                self.undo_move(current_basic_move_details, current_player)
                if move_branch_eval < min_eval:
                    min_eval = move_branch_eval; best_full_move_details = (move, best_remove_for_this_move)
                beta = min(beta, min_eval)
                if beta <= alpha: break
            return min_eval, best_full_move_details

    def move_creates_mill_heuristic(self, move, player):
        to_pos, from_pos = move
        if self.board[to_pos] != 0: return False
        original_from_val = 0
        if from_pos != -1:
             if self.board[from_pos] != player: return False
             original_from_val = self.board[from_pos]
             self.board[from_pos] = 0
        self.board[to_pos] = player
        forms_mill = self.forms_mill(to_pos, player)
        self.board[to_pos] = 0
        if from_pos != -1:
            self.board[from_pos] = original_from_val
        return forms_mill

    def _place_bomb(self, player_id, position):
        self.next_bomb_id += 1
        bomb_data = {'id': self.next_bomb_id, 'player_id': player_id, 'position': position, 'timer': self.BOMB_INITIAL_TIMER}
        self.bombs_on_board.append(bomb_data)
        
        pos_coord = self.coordinates.get(position, f"?({position})")
        if player_id == 1:
            self.player_bomb_available = False
            print(f"Player placed Time Bomb (ID {bomb_data['id']}) on their piece at {pos_coord}.")
            self.last_player_move = (position, -2, None)
        else:
            self.ai_bomb_available = False
            print(f"AI placed Time Bomb (ID {bomb_data['id']}) on their piece at {pos_coord}.")
            self.last_ai_move = (position, -2, None)

    def _handle_bomb_updates_and_detonations(self, current_player_id_turn):
        bombs_detonated_this_round = False
        bombs_to_remove_after_detonation = []
        detonation_queue = []

        for bomb in self.bombs_on_board:
            if bomb['player_id'] == current_player_id_turn:
                bomb['timer'] -= 1
                if bomb['timer'] <= 0:
                    detonation_queue.append(bomb)
        
        if detonation_queue:
            bombs_detonated_this_round = True
            print("\n--- Bomb Detonation Phase ---")
            self.display_board()
            time.sleep(1)

            for bomb_to_detonate in detonation_queue:
                self._detonate_bomb(bomb_to_detonate)
                bombs_to_remove_after_detonation.append(bomb_to_detonate)
            
            for btd in bombs_to_remove_after_detonation:
                if btd in self.bombs_on_board:
                    self.bombs_on_board.remove(btd)
            
            print("--- Detonation Phase Complete ---")
        
        return bombs_detonated_this_round

    def _detonate_bomb(self, bomb_info):
        bomb_pos = bomb_info['position']
        bomb_owner_str = "Player's" if bomb_info['player_id'] == 1 else "AI's"
        bomb_coord = self.coordinates.get(bomb_pos, f"?({bomb_pos})")
        
        print(f"\nKABOOM! {bomb_owner_str} Time Bomb (ID {bomb_info['id']}) at {bomb_coord} explodes!")
        
        pieces_removed_count = 0
        for adj_pos in self.adjacent_positions[bomb_pos]:
            if self.board[adj_pos] != 0:
                adj_coord = self.coordinates.get(adj_pos, f"?({adj_pos})")
                # --- Remove bomb if present on adjacent piece ---
                for bomb in list(self.bombs_on_board):
                    if bomb['position'] == adj_pos:
                        self.bombs_on_board.remove(bomb)
                        owner_str = "Player's" if bomb['player_id'] == 1 else "AI's"
                        print(f"  {owner_str} Time Bomb (ID {bomb['id']}) at {adj_coord} was destroyed in the blast and disarmed.")
                        time.sleep(0.2)
                        break
                # --- END Remove bomb on adjacent ---
                if self.board[adj_pos] == 1:
                    print(f"  Player's piece 'O' at {adj_coord} destroyed and returned to place pool.")
                    self.board[adj_pos] = 0
                    self.player_pieces_on_board -= 1
                    self.player_pieces_to_place += 1
                    pieces_removed_count +=1
                elif self.board[adj_pos] == 2:
                    print(f"  AI's piece 'X' at {adj_coord} destroyed and returned to place pool.")
                    self.board[adj_pos] = 0
                    self.ai_pieces_on_board -= 1
                    self.ai_pieces_to_place += 1
                    pieces_removed_count +=1
        
        if pieces_removed_count == 0:
            print("  No pieces were in the blast radius.")
        
        time.sleep(0.5)

    def ai_move(self):
        if self.ai_bomb_available and self.ai_pieces_on_board > 0 and (self.phase > 1 or self.ai_pieces_to_place < 7):
            best_bomb_target_pos = -1
            best_bomb_score = -100

            ai_owned_positions = [i for i, piece_val in enumerate(self.board) if piece_val == 2]
            
            for my_pos in ai_owned_positions:
                if any(b['position'] == my_pos for b in self.bombs_on_board):
                    continue

                current_bomb_score = 0
                opponent_adj_hit = 0
                own_adj_hit = 0
                for adj_pos in self.adjacent_positions[my_pos]:
                    if self.board[adj_pos] == 1:
                        opponent_adj_hit += 1
                    elif self.board[adj_pos] == 2:
                        own_adj_hit += 1
                
                current_bomb_score = (opponent_adj_hit * 2) - (own_adj_hit * 3)

                if current_bomb_score > best_bomb_score and opponent_adj_hit > 0 :
                    if opponent_adj_hit > 0 and (current_bomb_score > 0 or (opponent_adj_hit >=2 and own_adj_hit <=1 )):
                       best_bomb_score = current_bomb_score
                       best_bomb_target_pos = my_pos
            
            if best_bomb_target_pos != -1 and best_bomb_score >= 1:
                print(f"AI is thinking about a bomb... (Score: {best_bomb_score})")
                time.sleep(0.5)
                self._place_bomb(2, best_bomb_target_pos)
                print(f"AI uses its Time Bomb on piece at {self.coordinates.get(best_bomb_target_pos)}.")
                time.sleep(1.5)
                return

        depth = 3
        total_pieces_left = self.player_pieces_on_board + self.ai_pieces_on_board + self.player_pieces_to_place + self.ai_pieces_to_place
        if total_pieces_left <= 10: depth = 4
        if total_pieces_left <= 6: depth = 5
        if self.phase == 3: depth = max(depth, 5)

        print(f"AI is thinking (Depth: {depth})...")
        start_time = time.time()
        score, best_full_move_details = self.alpha_beta_search(depth, float('-inf'), float('inf'), True)
        end_time = time.time()
        print(f"AI decided in {end_time - start_time:.2f} seconds (Eval: {score:.1f}).")

        if best_full_move_details:
            best_move, best_remove_pos = best_full_move_details
            if best_move is None:
                 print("AI Error: Search returned None for best move.")
                 valid_moves = self.get_valid_moves(2)
                 if valid_moves:
                     print("AI attempting random recovery move...")
                     best_move = random.choice(valid_moves)
                     best_remove_pos = None 
                 else:
                     print("AI Error: No valid moves available for recovery.")
                     return 
            move_coord_str = self.format_move((best_move[0], best_move[1], None))
            mill_formed = self.make_move(best_move, 2)
            print(f"AI chooses: {self.format_move(self.last_ai_move)}")
            self.display_board()
            time.sleep(1)

            if mill_formed:
                print("AI formed a mill!")
                removal_target = None
                if best_remove_pos is not None and self.is_valid_removal(best_remove_pos, 2):
                    removal_target = best_remove_pos
                else:
                    remove_options = [p for p in range(24) if self.is_valid_removal(p, 2)]
                    if remove_options:
                        removal_target = random.choice(remove_options)
                        print(f"AI fallback removal target: {self.coordinates.get(removal_target, '?')}.")
                    else: print("AI formed mill, but no valid piece to remove?")

                if removal_target is not None:
                    if self.perform_removal(removal_target, 2):
                        print(f"AI removed piece at {self.coordinates.get(removal_target, '?')}.")
                        self.display_board() 
                        time.sleep(1.5)
                    else: print(f"AI Error: Failed to perform intended removal at {removal_target}")
                else: time.sleep(1)
        else:
            print("AI has no valid moves.")

    def is_game_over(self):
        player_done_placing = self.player_pieces_to_place == 0
        ai_done_placing = self.ai_pieces_to_place == 0
        if player_done_placing and self.player_pieces_on_board < 3:
            self.winner = "AI"; return True
        if ai_done_placing and self.ai_pieces_on_board < 3:
            self.winner = "Player"; return True
        player_can_move = bool(self.get_valid_moves(1))
        ai_can_move = bool(self.get_valid_moves(2))
        if player_done_placing and not player_can_move:
            self.winner = "AI"; return True
        if ai_done_placing and not ai_can_move:
            self.winner = "Player"; return True
        self.winner = None
        return False

    def get_coord_input(self, prompt):
        while True:
            coord = input(prompt).strip().upper()
            if coord in self.position_map:
                return self.position_map[coord]
            else:
                print("Invalid coordinate. Use format like 'A1', 'D7', etc.")

    def play_game(self):
        game_running = True
        while game_running:
            current_player_for_bomb_tick = 1 if self.player_turn else 2
            detonations_occurred = self._handle_bomb_updates_and_detonations(current_player_for_bomb_tick)
            
            if detonations_occurred:
                print("\n--- Post-Detonation Board State ---")
                self.display_board()
                time.sleep(2)
                if self.is_game_over():
                    print(f"\n--- Game Over due to Bomb Detonation! ---")
                    print(f"Winner: {self.winner}")
                    game_running = False
                    break 
            
            if self.is_game_over():
                self.display_board()
                print(f"\n--- Game Over! ---")
                print(f"Winner: {self.winner}")
                game_running = False; break
            
            self.display_board()

            if self.player_turn:
                import copy
                self._undo_stack.append({
                    'board': self.board[:],
                    'phase': self.phase,
                    'player_pieces_to_place': self.player_pieces_to_place,
                    'ai_pieces_to_place': self.ai_pieces_to_place,
                    'player_pieces_on_board': self.player_pieces_on_board,
                    'ai_pieces_on_board': self.ai_pieces_on_board,
                    'last_player_move': self.last_player_move,
                    'last_ai_move': self.last_ai_move,
                    'winner': self.winner,
                    'player_turn': self.player_turn,
                    'player_bomb_available': self.player_bomb_available,
                    'ai_bomb_available': self.ai_bomb_available,
                    'bombs_on_board': copy.deepcopy(self.bombs_on_board),
                    'next_bomb_id': self.next_bomb_id,
                })
                print("\n--- Player's Turn (O) ---")
                made_move = False; mill_formed = False
                is_placing = self.player_pieces_to_place > 0
                is_flying = (not is_placing) and (self.player_pieces_on_board <= 3)
                phase_name = "Fly" if is_flying else "Move"
                phase_num_str = "3" if is_flying else "2"

                while not made_move:
                    valid_moves = self.get_valid_moves(1)
                    can_make_normal_move = bool(valid_moves)
                    
                    actions_prompt = []
                    if is_placing: actions_prompt.append("(P)lace piece")
                    else: actions_prompt.append("(M)ove piece")

                    if self.player_bomb_available and self.player_pieces_on_board > 0:
                        actions_prompt.append("(B)omb")
                    
                    if not can_make_normal_move and not (self.player_bomb_available and self.player_pieces_on_board > 0) :
                         print("No valid moves or actions! Player is stuck.")
                         self.winner = "AI"
                         game_running = False; break


                    action_choice_str = input(f"Choose action: {', '.join(actions_prompt)}: ").strip().upper()

                    if action_choice_str == 'B' and self.player_bomb_available and self.player_pieces_on_board > 0:
                        print("Select one of your pieces to arm with a Time Bomb.")
                        pos_to_bomb = self.get_coord_input("Enter position of YOUR piece to arm: ")
                        if self.board[pos_to_bomb] == 1:
                            is_already_bombed = any(b['position'] == pos_to_bomb for b in self.bombs_on_board)
                            if not is_already_bombed:
                                self._place_bomb(1, pos_to_bomb)
                                made_move = True
                            else:
                                print("That piece already has a bomb or is an invalid choice. Try again.")
                        else:
                            print("That is not your piece or the spot is empty. Try again.")

                    elif (action_choice_str == 'P' and is_placing) or \
                         (action_choice_str == 'M' and not is_placing) or \
                         (action_choice_str == '' and can_make_normal_move):

                        if not can_make_normal_move:
                            print("No standard moves available. If you have a bomb, try using it.")
                            continue

                        if is_placing:
                            print(f"Phase 1: Place piece ({self.player_pieces_to_place} left)")
                            pos = self.get_coord_input("Enter position to place (e.g., A1): ")
                            if self.is_valid_place(pos): 
                                mill_formed = self.make_move((pos, -1), 1); made_move = True
                            else: print("Invalid position. Try again.")
                        else:
                            print(f"Phase {phase_num_str} ({phase_name}): Select piece and destination")
                            from_pos = self.get_coord_input("Enter position of piece to move: ")
                            if self.board[from_pos] != 1: print("Not your piece."); continue
                            
                            possible_destinations = []
                            for move_option_to, move_option_from in valid_moves:
                                if move_option_from == from_pos:
                                    possible_destinations.append(move_option_to)
                            
                            if not possible_destinations: print("This piece has no valid moves."); continue
                            
                            valid_dest_coords = sorted([self.coordinates[p] for p in possible_destinations])
                            print(f"Valid destinations for {self.coordinates[from_pos]}: {', '.join(valid_dest_coords)}")
                            to_pos = self.get_coord_input("Enter destination position: ")
                            
                            if (to_pos, from_pos) in valid_moves: 
                                mill_formed = self.make_move((to_pos, from_pos), 1); made_move = True
                            else: print("Invalid destination. Try again.")
                    else:
                        print("Invalid action choice. Try again.")

                if not game_running: break 

                if made_move and mill_formed:
                    self.display_board(); print("\nMill formed! Select an opponent's piece (X) to remove.")
                    removed_piece_successfully = False
                    while not removed_piece_successfully:
                        valid_removals = [p for p in range(24) if self.is_valid_removal(p, 1)]
                        if not valid_removals: print("No valid pieces to remove."); time.sleep(2); break 
                        valid_removal_coords = sorted([self.coordinates[p] for p in valid_removals])
                        print(f"Valid removal targets: {', '.join(valid_removal_coords)}")
                        remove_pos = self.get_coord_input("Enter position to remove: ")
                        if self.perform_removal(remove_pos, 1):
                            print(f"Removed piece at {self.coordinates[remove_pos]}."); removed_piece_successfully = True
                        else: print("Invalid removal choice. Try again.")
                
                if made_move:
                     print("\n--- Player's Turn End ---")
                     time.sleep(0.5 if not mill_formed else 1.5)

                     self.display_board()
                     if self.player_undos_left > 0:
                         undo_choice = input(f"\nYou have {self.player_undos_left} undos left. Undo this move? (Y/N): ").strip().upper()
                         if undo_choice == 'Y':
                             if self._undo_stack:
                                 prev = self._undo_stack.pop()
                                 self.board = prev['board'][:]
                                 self.phase = prev['phase']
                                 self.player_pieces_to_place = prev['player_pieces_to_place']
                                 self.ai_pieces_to_place = prev['ai_pieces_to_place']
                                 self.player_pieces_on_board = prev['player_pieces_on_board']
                                 self.ai_pieces_on_board = prev['ai_pieces_on_board']
                                 self.last_player_move = prev['last_player_move']
                                 self.last_ai_move = prev['last_ai_move']
                                 self.winner = prev['winner']
                                 self.player_turn = prev['player_turn']
                                 self.player_bomb_available = prev['player_bomb_available']
                                 self.ai_bomb_available = prev['ai_bomb_available']
                                 import copy
                                 self.bombs_on_board = copy.deepcopy(prev['bombs_on_board'])
                                 self.next_bomb_id = prev['next_bomb_id']
                                 self.player_undos_left -= 1
                                 print("\nMove undone. Your turn again.")
                                 self.display_board()
                                 continue
                             else:
                                 print("No undo state available.")

            else:
                print("\n--- AI's Turn (X) ---")
                self.ai_move()
                print("\n--- AI's Turn End ---"); time.sleep(1)

            if game_running: self.player_turn = not self.player_turn

if __name__ == "__main__":
    game = NineMensMorris()
    try:
        game.play_game()
    except KeyboardInterrupt: print("\nGame interrupted.")
    finally:
        if game.winner: print(f"\nFinal Result: {game.winner} wins!")
        elif game.is_game_over() and game.winner:
            print(f"\nFinal Result: {game.winner} wins!")

        print("\nThank you for playing!")