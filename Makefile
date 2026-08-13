.PHONY: install check check-full sync-supply-chain

install:
	python3 -m pip install -r requirements.txt

check:
	bash scripts/check.sh

check-full: check
	python3 scripts/sync_supply_chain.py --check
	python3 scripts/validate_problem_library.py
	python3 scripts/test_problem_library.py
	python3 scripts/validate_literature.py

sync-supply-chain:
	python3 scripts/sync_supply_chain.py
