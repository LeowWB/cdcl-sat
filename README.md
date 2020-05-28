## cdcl-sat

### Introduction

This repository contains the code for a sat-solver based off the CDCL
algorithm. It has a number of heuristics in place to improve efficiency,
such as 1-UIP, random restarts, and learned clause forgetting. 

### Usage

In order to run the code, you will require both Python 3 and the `networkx`
library. The script can then be run with:

```sh
python src/cdcl.py <formula.cnf>
```

where `<formula.cnf>` is a DIMACS-encoded file.

