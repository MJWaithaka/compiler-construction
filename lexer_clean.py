import string

_KW_TRANSITIONS = {
    'A': {'l': 'B', 
          'i': 'C', 
          'w': 'D'},

    'B': {'e': 'H'},
    'C': {'f': 'I'},
    'D': {'h': 'J'},
    'H': {'t': 'K'},
    'J': {'i': 'L'},
    'L': {'l': 'M'},
    'M': {'e': 'N'},
}

_LETTERS   = set(string.ascii_letters + '_')
_DIGITS    = set(string.digits)
_ID_CHARS  = _LETTERS | _DIGITS
_OP_CHARS  = set('=+<(){};')

_ACCEPTING = {
    'B': 'ID', 'C': 'ID', 'D': 'ID',
    'H': 'ID', 'J': 'ID', 'L': 'ID', 'M': 'ID',
    'E': 'ID',
    'I': 'KW', 'K': 'KW', 'N': 'KW',
    'F': 'NUM',
    'G': 'OP',
}

def _next_state(state, char):
    if state in _KW_TRANSITIONS and char in _KW_TRANSITIONS[state]:
        return _KW_TRANSITIONS[state][char]

    if state == 'A':
        if char in _LETTERS:  return 'E'
        if char in _DIGITS:   return 'F'
        if char in _OP_CHARS: return 'G'

    elif state in ('B', 'C', 'D', 'H', 'J', 'L', 'M'):
        if char in _ID_CHARS: return 'E'

    elif state in ('E', 'I', 'K', 'N'):
        if char in _ID_CHARS: return 'E'

    elif state == 'F':
        if char in _DIGITS: return 'F'

    return None


def lex(source):
    tokens = []
    i = 0
    n = len(source)

    while i < n:
        if source[i].isspace():
            i += 1
            continue

        state          = 'A'
        last_acc_state = None
        last_acc_pos   = -1
        j              = i

        while j < n:
            nxt = _next_state(state, source[j])
            if nxt is None:
                break
            state = nxt
            if state in _ACCEPTING:
                last_acc_state = state
                last_acc_pos   = j
            j += 1

        if last_acc_state is not None:
            lexeme = source[i : last_acc_pos + 1]
            tok_type = _ACCEPTING[last_acc_state]
            
            next_pos = last_acc_pos + 1
            if tok_type in ('NUM', 'ID', 'KW') and next_pos < n:
                nxt_char = source[next_pos]
                if not nxt_char.isspace() and nxt_char not in _OP_CHARS:
                    k = next_pos
                    while k < n and not source[k].isspace() and source[k] not in _OP_CHARS:
                        k += 1
                    err_kind = 'numeric' if tok_type == 'NUM' else 'identifier'
                    tokens.append(('ERR', f"Invalid {err_kind} format: '{source[i:k]}'"))
                    i = k
                    continue

            if tok_type in ('ID', 'KW') and len(lexeme) > 31:
                tokens.append(('ERR', f"Identifier exceeds length limit (31): '{lexeme}'"))
                i = last_acc_pos + 1
                continue
            if tok_type == 'NUM' and int(lexeme) > 2147483647:
                tokens.append(('ERR', f"Numeric literal out of bounds: '{lexeme}'"))
                i = last_acc_pos + 1
                continue

            tokens.append((tok_type, lexeme))
            i = last_acc_pos + 1
        else:
            tokens.append(('ERR', f"Illegal character: '{source[i]}'"))
            i += 1

    return tokens


if __name__ == '__main__':
    import sys
    
    filename = sys.argv[1] if len(sys.argv) > 1 else 'sample.js'
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            sample = f.read()
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        sys.exit(1)

    print("Source program")
    print("=" * 60)
    print(sample)
    print()
    print(f"{'#':<4} {'Token':<6} {'Lexeme'}")
    print("-" * 60)

    token_list = lex(sample)
    for idx, (tok, lex_) in enumerate(token_list, 1):
        print(f"{idx:<4} {tok:<6} {lex_!r}")

    print("-" * 60)
    print(f"Total tokens: {len(token_list)}")

    errors = [(i, t, l) for i, (t, l) in enumerate(token_list, 1) if t == 'ERR']
    if errors:
        print("\nLexical errors:")
        for pos, tok, lex_ in errors:
            print(f"  Token #{pos}: {tok} {lex_!r}")
    else:
        print("No lexical errors.")