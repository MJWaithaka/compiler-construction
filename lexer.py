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
            tokens.append((_ACCEPTING[last_acc_state], lexeme))
            i = last_acc_pos + 1
        else:
            tokens.append(('ERR', source[i]))
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



