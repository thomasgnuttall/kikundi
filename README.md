## Kikundi

A python package for applying hierarchical clustering analysis to subgenre tags.

### Documentation

For an overview of the pipeline see `documentation/Pipeline.pdf`

### Installation

Kikundi is written in Python 3.5

To install package:
`pip install -e .`

### Usage Instructions

To run the pipeline

`python kikundi run-pipeline conf/setup.yaml`

Add the optional `--report` tag to write a graph of David Bouldin Index across multiple values of k

An example output can be found at `documentation/example_output.txt`

### Testing

To run tests:
`pytest`




Thomas Nuttall -  2019