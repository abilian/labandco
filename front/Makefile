.PHONY: test run clean lint


all: test lint-js


test: test-unit

test-unit:
	yarn run test:unit

# test-with-coverage:
# 	yarn run test-with-coverage
#

test-e2e:
	yarn run cypress run

clean:
	rm -rf node_modules dist tmp coverage yarn-error.log
	rm -rf tests/e2e/videos/ tests/e2e/screenshots/

rebuild: clean
	yarn
	make build

build:
	yarn run build

# consistent name with other projects.
lint: lint-js

lint-js:
	yarn run lint

lint-ts:
	npx tsc

format:
	npx prettier --write --trailing-comma es5 \
		'*.js' 'src/**/*.vue' 'src/**/*.js' 'tests/**/*.js' \
		'sass/*.scss'
