CXX ?= g++
CXXFLAGS ?= -O3 -DNDEBUG -std=c++20 -Wall -Wextra

.PHONY: all test download verify clean
all: build/solver
build/solver: src/solver.cpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $< -o $@
test: all
	python -m unittest discover -s tests -v
download:
	python scripts/download.py
verify: all
	python -m aocbb verify --report reports/verification.json
clean:
	rm -rf build
