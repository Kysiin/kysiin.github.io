// bench.h - headless parameter sweep used for the experiments in the report
#pragma once
#include <string>

// Runs all benchmark cases and writes a CSV file. Returns false on I/O error.
bool runBench(const std::string& outPath);
