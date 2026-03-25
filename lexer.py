"""
Group 19 — Mini-JavaScript Lexer
Implemented directly from the verified Subset Construction DFA.

Token types
-----------
KW   keyword:    let | if | while
ID   identifier: [a-zA-Z_][a-zA-Z0-9_]*
NUM  number:     [0-9]+
OP   operator & punctuation: = + < ( ) { } ;
ERR  lexical error: unrecognised character (scanner continues)
"""

import string

# ---------------------------------------------------------------------------
# DFA transition table  (keyword paths only — character classes handled below)
# ---------------------------------------------------------------------------
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

# Accepting states and their token types
_ACCEPTING = {
    # Intermediate identifier-prefix states — accept as ID if nothing longer matches
    'B': 'ID', 'C': 'ID', 'D': 'ID',
    'H': 'ID', 'J': 'ID', 'L': 'ID', 'M': 'ID',
    # Pure identifier
    'E': 'ID',
    # Keywords (priority over ID by virtue of being listed in DFA)
    'I': 'KW', 'K': 'KW', 'N': 'KW',
    # Number
    'F': 'NUM',
    # Operator / punctuation
    'G': 'OP',
}

def _next_state(state, char):
    """Return the next DFA state, or None if no valid transition exists."""
    # Keyword-path transitions (exact characters)
    if state in _KW_TRANSITIONS and char in _KW_TRANSITIONS[state]:
        return _KW_TRANSITIONS[state][char]

    if state == 'A':
        if char in _LETTERS:  return 'E'
        if char in _DIGITS:   return 'F'
        if char in _OP_CHARS: return 'G'

    elif state in ('B', 'C', 'D', 'H', 'J', 'L', 'M'):
        # On any id-char that did not match the keyword path → fall to pure ID state
        if char in _ID_CHARS: return 'E'

    elif state in ('E', 'I', 'K', 'N'):
        # Already in / past keyword — keep consuming identifier characters
        if char in _ID_CHARS: return 'E'

    elif state == 'F':
        if char in _DIGITS: return 'F'

    return None   # ERR sink — no valid transition


def lex(source):
    """
    Tokenise *source* using maximal munch on the verified DFA.

    Returns a list of (token_type, lexeme) tuples.
    Unrecognised characters produce an ERR token and scanning resumes
    at the next character rather than crashing.
    """
    tokens = []
    i = 0
    n = len(source)

    while i < n:
        # Skip whitespace
        if source[i].isspace():
            i += 1
            continue

        # ── Check for comments (Unmatched string/comment error) ───────────
        if source.startswith('/*', i):
            end_idx = source.find('*/', i + 2)
            if end_idx == -1:
                # Lexical error: Unmatched comment
                tokens.append(('ERR', "Unmatched comment: " + source[i:i+15] + "..."))
                break # Reached EOF
            else:
                i = end_idx + 2
                continue

        # ── Check for strings (Unmatched string error) ────────────────────
        if source[i] == '"':
            end_idx = source.find('"', i + 1)
            # Find next newline to bound the string search
            nl_idx = source.find('\n', i + 1)
            if end_idx == -1 or (nl_idx != -1 and nl_idx < end_idx):
                # Lexical error: Unmatched string within the line
                err_text = source[i:nl_idx] if nl_idx != -1 else source[i:]
                tokens.append(('ERR', "Unmatched string: " + err_text))
                if nl_idx != -1:
                    i = nl_idx
                else:
                    break
                continue
            else:
                tokens.append(('STR', source[i:end_idx+1]))
                i = end_idx + 1
                continue

        # ── Maximal-munch scan ────────────────────────────────────────────
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

        # ── Emit token or report error ────────────────────────────────────
        if last_acc_state is not None:
            lexeme = source[i : last_acc_pos + 1]
            tok_type = _ACCEPTING[last_acc_state]
            
            # 1 & 4 & 5. Invalid suffix check (e.g. 10f, 3num, 12$34)
            # A number should generally be followed by an operator, space, or EOF
            next_pos = last_acc_pos + 1
            if tok_type == 'NUM' and next_pos < n:
                nxt_char = source[next_pos]
                if not nxt_char.isspace() and nxt_char not in _OP_CHARS:
                    # Consume the malformed token until next space or operator
                    k = next_pos
                    while k < n and not source[k].isspace() and source[k] not in _OP_CHARS:
                        k += 1
                    tokens.append(('ERR', f"Invalid numeric format: '{source[i:k]}'"))
                    i = k
                    continue

            # 2. Exceeding length limits
            if tok_type == 'ID' and len(lexeme) > 31:
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
            # 2. Appearance of illegal characters
            tokens.append(('ERR', f"Illegal character: '{source[i]}'"))
            i += 1

    return tokens


# ---------------------------------------------------------------------------
# Entry point — scan the sample program and display results
# ---------------------------------------------------------------------------
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

    # Verify no ERR tokens in the clean sample
    errors = [(i, t, l) for i, (t, l) in enumerate(token_list, 1) if t == 'ERR']
    if errors:
        print("\nLexical errors:")
        for pos, tok, lex_ in errors:
            print(f"  Token #{pos}: {tok} {lex_!r}")
    else:
        print("No lexical errors.")



