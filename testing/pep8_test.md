1. ISSUE: F401 [*] imported but unused
   SOLUTION: Removed all references to imports declared but not used

2. ISSUE: E501 Line too long
   SOLUTION: Splits line of code where appropriate

3. ISSUE: F811 [*] Redefinition of unused
   SOLUTION: Removed duplicate & unused imports

4. ISSUE: E401 [*] Multiple imports on one line
   --> better_billing/lint_probe.py:1:1
   SOLUTION: Split imports

5. ISSUE: E702 Multiple statements on one line (semicolon)
   --> better_billing/settings.py:12:31
   SOLUTION: Correct syntax

6. ISSUE: E402 Module level import not at top of file
   --> better_billing/settings.py:13:1
   SOLUTION: Move OS and dj_database to top

7. ISSUE: W293 [*] Blank line contains whitespace
   --> better_billing/settings.py:45:1
   SOLUTION: Remove whitespaces |

8. ISSUE: W292 [*] No newline at end of file
   --> better_billing/urls.py:30:52
   SOLUTION : Add trailing newline




<!-- LEAVE UNTIL LAST :) -->
F811 Redefinition of unused `record_time` from line 73
--> better_bill_project/views.py:357:5
|
356 | @login_required
357 | def record_time(request):
| ^^^^^^^^^^^ `record_time` redefined here
358 | # Who can see everything? (Partners/Admins – reusing your post_invoice perm)
359 | is_partner = request.user.has_perm("better_bill_project.post_invoice") or request.user.is_superuser
|
::: better_bill_project/views.py:73:5
|
72 | # Time Entry Form
73 | def record_time(request):
| ----------- previous definition of `record_time` here
74 | recent_entries = TimeEntry.objects.select_related(
75 | "matter", "fee_earner"
|
help: Remove definition: `record_time`

