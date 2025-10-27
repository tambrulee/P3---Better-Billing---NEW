## PEP8 Testing Errors & Solutions

1. ISSUE: F401 [*] imported but unused
   SOLUTION: Removed all references to imports declared but not used

2. ISSUE: E501 Line too long
   SOLUTION: Splits line of code where appropriate

3. ISSUE: F811 [*] Redefinition of unused
   SOLUTION: Removed duplicate & unused imports

4. ISSUE: E401 [*] Multiple imports on one line
   SOLUTION: Split imports

5. ISSUE: E702 Multiple statements on one line (semicolon)
   SOLUTION: Correct syntax

6. ISSUE: E402 Module level import not at top of file
   SOLUTION: Move OS and dj_database to top of settings.py

7. ISSUE: W293 [*] Blank line contains whitespace
   SOLUTION: Remove whitespaces |

8. ISSUE: W292 [*] No newline at end of file
   SOLUTION : Add trailing newline
