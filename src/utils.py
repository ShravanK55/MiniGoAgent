def get_board_from_state(state, board_size):
    """
    Method to get a board from an encoded state.

    Args:
        state(str): Encoded state of the board.
        board_size(int): Size of the Go board.

    Returns:
        (board): Equivalent board.

    """
    board = [[int(state[i * board_size + j]) for j in range(board_size)] for i in range(board_size)]
    return board


def get_encoded_state(board, board_size):
    """
    Method to get the encoded state of a Go board.

    Args:
        board(list): Board to get the state for.
        board_size(int): Size of the Go board.

    """
    state = ""
    for i in range(board_size):
        for j in range(board_size):
            state += str(board[i][j])

    return state


def get_rotated_state(state, size):
    """
    Method to get a board rotated clockwise by 90 degrees.

    Args:
        state(str): Encoded state of the board to get the rotation of.
        size(int): Size of the board.

    Returns:
        (rotated_state): State rotated by 90 degrees.

    """
    board = get_board_from_state(state, size)
    rotated_board = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            rotated_board[j][size - i - 1] = board[i][j]

    return get_encoded_state(rotated_board, size)


def get_flipped_state(state, size, flip_horizontally, flip_vertically):
    """
    Method to get a board from a state that is horizontally/vertically flipped.

    Args:
        state(state): State of the board to horizontally/vertically flip.
        size(int): Size of the board.
        flip_horizontally(bool): Whether to flip the board horizontally.
        flip_vertically(bool): Whether to flip the board vertically.

    Returns:
        (flipped_state): Horizontally/vertically flipped state.

    """
    board = get_board_from_state(state, size)
    flipped_board = [[0 for _ in range(size)] for _ in range(size)]

    for i in range(size):
        for j in range(size):
            target_row = size - i - 1 if flip_vertically else i
            target_column = size - j - 1 if flip_horizontally else j
            flipped_board[target_row][target_column] = board[i][j]

    return get_encoded_state(flipped_board, size)


def get_equivalent_action(action, board_size, flip_horizontally=False, flip_vertically=False, num_rotations=0,
                          backwards=True):
    """
    Method to get an equivalent action when the Go board is flip horizontally, vertically and rotated.

    Args:
        action(tuple): Action to get the equivalent for.
        board_size(int): Size of the Go board.
        flip_horizontally(bool): Whether to flip the action horizontally. Defaults to False.
        flip_vertically(bool): Whether to flip the action vertically. Defaults to False.
        num_rotations(int): Number of clockwise rotations to apply to the action. Defaults to 0.
        backwards(bool): Whether to apply transformations in the opposite order. Defaults to True.

    Returns:
        (equivalent_action): Action after flips and rotations.

    """
    equivalent_action = (action[0], action[1])

    if backwards:
        for _ in range(num_rotations):
            equivalent_action = (equivalent_action[1], board_size - equivalent_action[0] - 1)

        if flip_vertically:
            equivalent_action = (board_size - equivalent_action[0] - 1, equivalent_action[1])

        if flip_horizontally:
            equivalent_action = (equivalent_action[0], board_size - equivalent_action[1] - 1)

    else:
        if flip_horizontally:
            equivalent_action = (equivalent_action[0], board_size - equivalent_action[1] - 1)

        if flip_vertically:
            equivalent_action = (board_size - equivalent_action[0] - 1, equivalent_action[1])

        for _ in range(num_rotations):
            equivalent_action = (equivalent_action[1], board_size - equivalent_action[0] - 1)


    return equivalent_action
