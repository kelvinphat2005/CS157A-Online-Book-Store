# Andy's authentication update: verification

Tested November 24, 2026. The scope is the login/registration interface,
connection to the existing session backend, logout, and restricted-page access.

## Result

| Verification | Result |
| --- | --- |
| Automated behavior tests with an isolated SQL test adapter | 66 passed |
| Live SQL tests using the actual MySQL Connector/Python and original Schema.sql | 8 passed |
| Chromium browser workflow and responsive checks | 37 passed |
| Final layout checks, including 100-character unbroken names | 10 passed |

No failed tests remain.

## Environment and limits

- Python 3.12.14; Flask 3.1.3; Werkzeug 3.1.9.
- MySQL Connector/Python 26.10.0; pytest 9.2.0.
- Live database: MariaDB 10.11.18, using MySQL's client protocol.
- Browser: Chromium 150, headless.
- Browser widths: 375, 768, and 1440 pixels.

The live checks used a temporary local MariaDB server, not an Oracle MySQL server
or your team's existing database. The application remains configured for MySQL.
Repeat the included MySQL tests against your local server before merging. The
code has not been tested under your exact Python 3.14 environment.

The isolated tests use a SQLite-backed connector adapter that translates only
parameter placeholders. SQLite is a TEST dependency from Python's standard
library; it is not an application database or a technology-stack change.
The eight live tests execute the actual SQL through MySQL Connector/Python,
import all six original tables into a random test database, and remove that
test database afterwards.

## Behavior verified

- All public pages render without opening a database connection.
- Signup stores a normalized email and a hash rather than the supplied password.
- Public signup always creates a customer, even with a submitted admin role.
- Empty/invalid fields, oversized input, short passwords, mismatches, and duplicate
  emails return useful form errors without creating unintended accounts.
- Duplicate-insert races and database errors roll back and show safe messages.
- Valid login establishes the expected session; invalid login does not.
- Old session fields and form tokens are discarded at login.
- The original destination is preserved for local URLs; external and ambiguous
  redirect targets are ignored.
- Guests cannot access orders or staff by typing the URL directly.
- Customers can access orders but receive 403 on staff.
- Admins can access staff and see its navigation link.
- Logout requires a POST form/token, clears the login session, and removes access.
- CSRF tokens are checked for login, registration, and logout. Missing, invalid,
  cross-session, stale, and non-ASCII invalid tokens fail safely.
- User text is escaped; passwords are not prefilled after an error.
- Database cursors/connections close at the end of requests.
- Account HTML is not cached; session cookies use HttpOnly and SameSite=Lax.

## Browser verification

Real browser form submissions covered:

1. Signup with a mismatched confirmation, followed by a corrected signup.
2. A failed login, followed by a successful customer login.
3. Customer navigation, direct order access, and a direct staff URL returning 403.
4. Logout followed by an attempted protected-page visit.
5. Admin login and staff navigation.
6. Password Show/Hide buttons.
7. Complete mobile login/navigation/logout.
8. Login with JavaScript disabled.
9. No horizontal overflow at all three viewport widths on home, login, and signup.
10. No browser JavaScript errors.

Final visual inspection covered desktop and mobile forms and the decorative book
artwork. Browser screenshots were used only for internal QA and are not included.
Machine-readable pytest and browser results are in the package's verification folder.

## Functional boundaries

Catalog contents, real order history, checkout, inventory/order management,
reviews, and the 15-rows-per-table sample data are separate team work.
The catalog, orders, and staff pages included here are labeled placeholders;
their purpose in this update is consistent navigation and access testing.
Schema.sql and the existing relational-schema document are unchanged.

## Reproduce

Follow START_HERE_ANDY.md for setup and manual checks. Then:

    python -m pip install -r requirements-dev.txt
    python -m pytest -q

This runs 66 tests; eight live tests are skipped by default. Enable those only
when a local MySQL server is available, using BOOKSTORE_TEST_MYSQL=1 and the
MYSQL_HOST, MYSQL_PORT, MYSQL_USER, and MYSQL_PASSWORD variables in the guide.

## Useful references

- https://flask.palletsprojects.com/en/stable/tutorial/views/
- https://flask.palletsprojects.com/en/stable/testing/
- https://flask.palletsprojects.com/en/stable/web-security/
- https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
