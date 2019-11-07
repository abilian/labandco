End-to-end tests written with TestCafe: https://devexpress.github.io/testcafe/documentation/

They test the integration of the application (front end loading,
connecting and working as expected).

These tests are not currently under CI.

To run manually:

- Start server (`make run` at the top)
- Run tests (`npx testcafe chrome tests/e2e`)
