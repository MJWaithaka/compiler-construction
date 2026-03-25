/* Valid normal assignment */
let limit = 10;

/* 1. Exceeding Identifier Length (> 31 chars) */
let this_is_a_very_long_variable_name_that_will_fail = 1;

/* 2. Exceeding Number Limit (> 2147483647) */
let too_big = 9999999999;

/* 3. Illegal character */
let bad = @;

/* 4. Invalid numeric format / spelling error (Starts with number) */
let invalid_start = 3num;

/* 5. Invalid numeric format (Suffix error) */
let suffix_err = 10f;

/* 6. Incorrect character inside a number */
let bad_num = 12$34;

/* 7. Unmatched string (missing closing quote on line) */
let str = "this string never ends

/* 8. Unmatched comment (missing closing marker) - Must be at end! */
/* We forgot to close this comment block...
    let final = 0;
