# What is an embedding

A way of representing data as points in space where the locations are semanically meaningful.

## How are sentence embeddings computed?

Simple method: emed each word seperately, and take a sum of mean of all the word embeddings.

Modern embeddings:

- Use a transformer neural network to compute a context-aware representation of each word, then take an average of the context-aware representations.

- Compute embeddings for each token (e.g. sub-word) rather than word. Enables algorithm to work even for novel words and misspelt words ("Life, the unverse and everything.")

Training the transformer network (contrastive learning):

- Given a dataset of pairts of "similar" sentences, tune neural network to move similar sentence's embeddings together, and dissimilar sentence's embeddings apart.

## Applications

- Anomaly/Outlier detection
- Classification

## Temperature

It controls the randomness

## Top k

Sample from token with the top k probablities e.g. pick the top 3 tokens

## Top P

Sample from minimum set of tokens whose cumulative probability is greater or equal to P e.g. if top p is 0.75, we pick tokens for which sum of probabilities is >= 75%

## Priority:

(If all three are set, this is how they'll be used)
top K > top P > temperature

## Vector indexing

- HNSW (Hierarchical Navigable Small World) is a graph-based algorithm for approximate nearest neighbor (ANN) search in high-dimensional vector spaces.

- An Inverted File Index (IVF) is an Approximate Nearest Neighbor (ANN) algorithm that speeds up high-dimensional vector searches by grouping similar vectors into distinct clusters.
