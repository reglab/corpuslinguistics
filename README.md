# Corpus Enigmas and Contradictory Linguistics: Tensions Between Empirical Semantic Meaning and Judicial Interpretation
## Peter Henderson, Daniel E. Ho, Andrea Vallebueno, Cassandra Handan-Nader

This is the code repository for [Corpus Enigmas and Contradictory Linguistics: 
Tensions Between Empirical Semantic Meaning and Judicial Interpretation](https://scholarship.law.umn.edu/mjlst/vol25/iss2/12/).

**Citation:** Peter Henderson, Daniel E. Ho, Andrea Vallebueno & Cassandra Handan-Nader, 
_Corpus Enigmas and Contradictory Linguistics: Tensions Between Empirical Semantic Meaning and Judicial Interpretation_, 
25 Minn. J.L. Sci. & Tech. 127 (2024). Available at: https://scholarship.law.umn.edu/mjlst/vol25/iss2/12

## Set Up and Repository Structure
We run our analyses on the Corpus of Historical American English (COHA), which was used in a
corpus linguistics study by Lee et al. (2024) examining the original meaning of the word "income" 
under the 16th Amendment. 

The full text version of COHA that is required to run these analyses
can be obtained at [English-Corpora](https://www.english-corpora.org/coha/). Our code requires that
the following files be included in the `data` directory:

- `data/individual_texts`: A directory containing individual files for each document in COHA using the file name
structure `coha_{DOCUMENT ID}.txt`.
- `data/coha_document_metadata.json`: A JSON file with metadata for the documents that are in COHA. The object
for each document is identified by a Document ID, and contains the following attributes: number of words, 
genre, year, title and author. 
- `data/SSRN-id4560186Appendix.pdf` The PDF Appendix to "Corpus Linguistics and the Original Public Meaning 
of the Sixteenth Amendment" by Lee et al. (2023), which can be found 
[here](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4560186).

## Appendix C: Sample of Annotated Documents
We make available the sample of 131 annotated COHA documents that we manually classified as discussing foreign law or foreign contexts, 
or as discussing US legislative history, in the CSV file located at `outputs/AppendixC.csv` in this repository.

## References
Davies M, The 400 million word Corpus of Historical American English (1810–2009), 
Selected Papers from the Sixteenth International Conference on English Historical Linguistics 
(ICEHL 16), Pécs, 23–27 August 2010, eds Hegedűs I, Fodor A (John Benjamins Publishing, Amsterdam), Vol 325 (2010)

Nikhil Garg, Londa Schiebinger, Dan Jurafsky & James Zou, Word
Embeddings Quantify 100 Years of Gender and Ethnic Stereotypes, 115 PROC.
NAT’L ACAD. SCIS. E3635 (2018)

Thomas R. Lee, Lawrence B. Solum, James C. Phillips & Jesse A. Egbert, Corpus Linguistics and the Original Public Meaning of the Sixteenth
Amendment, 73 DUKE L.J. ONLINE 159, 164 (2024)

