1. ISSUE: F401 [*] imported but unused
SOLUTION: Removed all references to imports declared but not used

2. ISSUE: E501 Line too long 
SOLUTION: Splits line of code where appropriate

3. ISSUE: F811 [*] Redefinition of unused 
SOLUTION: Removed duplicate & unused imports

5. ISSUE: E401 [*] Multiple imports on one line
 --> better_billing/lint_probe.py:1:1
SOLUTION: Split imports

7. ISSUE: E702 Multiple statements on one line (semicolon)
  --> better_billing/settings.py:12:31
SOLUTION: Correct syntax

8. ISSUE: E402 Module level import not at top of file
  --> better_billing/settings.py:13:1
SOLUTION: Move OS and dj_database to top

9. ISSUE: W293 [*] Blank line contains whitespace
  --> better_billing/settings.py:45:1
SOLUTION: Remove whitespaces  |

10. ISSUE: W292 [*] No newline at end of file
  --> better_billing/urls.py:30:52
SOLUTION : Add trailing newline

