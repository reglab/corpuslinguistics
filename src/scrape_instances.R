# Extracts the table of income instances from Appendix A of "Appendices to
# Corpus Linguistics and the Original Public Meaning of the Sixteenth Amendment"
# Located at: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4560186

# 0. Working set up ----------------------------------------
library(stringr)
library(reshape)
library(pdftools)
library(tidyverse)
library(tidyr)
library(RJSONIO)

f# 1. Load data ----------------------------------
raw_data_fpath <- file.path('data', 'SSRN-id4560186Appendix.pdf')
data <- pdftools::pdf_text(raw_data_fpath)

# 2. Process ------------------------------------
income_pages <- 2:97  # Appendix A

# Drop definitions and expanded instances
data <- data[1:97]

instance.table <- data.frame()
for (counter in 1:length(data)){
  if (counter == 1) {
    next
  }
  
  page <- data[counter]
  
  # Get table
  page_table <- strsplit(page, 'Electronic copy available at')[[1]][1]
  if (grepl('Appendix ', page_table)) {
    page_table <- strsplit(page_table, 'known)\n')[[1]][2]
  }

  # Get each row
  rows <- strsplit(page_table, '\n')
  rows <- rows[[1]]
  
  # Drop rows without data
  rows <- grep(pattern='[A-Za-z]+', rows, value=T)
  
  # Get table 
  tab <- str_split_fixed(rows, '[ \t]{2,}', n=7)
  
  # Apply the column names
  table <- data.frame(tab)
  
  table.names <- c('Result Line', 'Year', 'Genre', 'Source', 'Indeterminate', 'Other1', 'Other2')
  if (all(table$X1 == '' )) {
    table <- dplyr::select(table, -X1)
    table.names <- c('Result Line', 'Year', 'Genre', 'Source', 'Indeterminate', 'Other1')
  }
  
  colnames(table) <- table.names
  
  # Drop extra text from concordance line
  table <- dplyr::filter(table, Genre %in% c('MAG', 'FIC', 'NEWS', 'NF/ACAD'))
  
  # Grab coder
  coders <- grep(pattern='\\s\\d$', rows, value=T)
  table$Coder <- str_sub(coders, -1, -1)
  
  # Grab Concordance line
  concordance <- c()
  for (c in  grep(pattern='\\s\\d$', rows, value=T)) {
    c <- strsplit(c, "\\s{2,}")[[1]]
    c <- c[length(c) - 1]
    concordance <- c(concordance, c)
  }
  table$concordance <- concordance
  table$Instance <- 'Income'
  
  # Append
  table <- dplyr::select(table, `Result Line`, Year, Genre, Source, Indeterminate, Coder, Instance, concordance)
  instance.table <- rbind(instance.table, table)
  
}

# 3. Add COHA text ---------------
metadata <- RJSONIO::fromJSON(
  '../data/coha_document_metadata.json', nullValue=NA)
metadata <- do.call(rbind, metadata)
metadata <- as.data.frame(metadata)
metadata$docid <- rownames(metadata)

# Filter metadata to 1900-1912
metadata <- dplyr::filter(metadata, year %in% 1900:1912)

# Flatten lists
metadata$year <- unlist(metadata$year)
metadata$title <- unlist(metadata$title)
metadata$`# words` <- unlist(metadata$`# words`)
metadata$genre <- unlist(metadata$genre)
metadata$Source <- unlist(metadata$title)
metadata$author <- unlist(metadata$author)
metadata$FullSource <- unlist(metadata$`Unnamed: 6`)

find_nonmag_docid <- function(source, source_year, metadata) {
  # Prepare the Source name for matching
  source_split <- gsub('([[:upper:]])', ' \\1', source)
  source_split <- str_trim(source_split)
  source_split <- strsplit(source_split, ' ')[[1]] 
  match_col <- 'Source'
  
  # Filter metadata
  source_metadata <- metadata %>% dplyr::filter(year == source_year)
  source_metadata$match <- 0
  
  for (substring in source_split) {
    source_metadata$match <- source_metadata$match + grepl(substring, source_metadata[[match_col]])
  }
  
  source_metadata <- source_metadata %>% dplyr::arrange(desc(match))
  
  return(list(DocId=source_metadata[1, 'docid'], Title=source_metadata[1, 'title'], FullSource=NA))
  
}

# Note: matching for magazines and news articles requires matching to 
# the underlying text in the document, since the instance table only
# provides the generic source
find_mag_docid <- function(source, source_year, source_text, metadata) {
  
  # Get Magazine/Newspaper name
  source_name <- convert_mag_name(source)
  
  # Filter metadata
  source_metadata <- metadata %>% 
    dplyr::filter(year == source_year) %>%
    dplyr::filter(!is.na(FullSource)) %>%
    dplyr::filter(grepl(source_name, FullSource, fixed=T))
  
  # Clean source text
  source_text <- gsub("([^A-Za-z0-9 ])+", "", source_text)
  source_text <- tolower(source_text)
  
  # Find match among possible documents
  source_metadata$match <- NA
  for (i in 1:dim(source_metadata)[1]) {
    docid <- source_metadata[i, 'docid']
    # Load document
    doc_text <- readLines(
      paste0('../data/individual_texts/coha_', docid, '.txt'), warn=F)
    
    doc_match <- 0
    for (w in strsplit(source_text, ' ')[[1]]) {
      doc_match <- doc_match + grepl(pattern=w, doc_text)
    }
    source_metadata[i, 'match'] <- doc_match
  }
  
  source_metadata <- source_metadata %>% dplyr::arrange(desc(match))
  
  return(
    list(DocId=source_metadata[1, 'docid'], 
         Title=source_metadata[1, 'title'], 
         FullSource=source_metadata[1, 'FullSource']))
  
}

convert_mag_name <- function(source) {
  name <- NA
  if (source == "Forum") name <- 'Forum'
  if (source == "PopSci") name <- 'Popular Science'
  if (source == "Outlook") name <- 'Outlook'
  if (source == "Cosmopolitan") name <- 'Cosmopolitan'
  if (source == "McClures") name <- "McClure's Magazine"
  if (source == "Atlantic") name <- 'The Atlantic Monthly'
  if (source == "Nation") name <- 'The Nation'
  if (source == "Harpers") name <- 'Harpers'
  if (source == "NYT-Reg") name <- 'New York Times'
  if (source == "NYT-Ed") name <- 'New York Times: (Editorials)'
  if (source == "Chicago") name <- 'Chicago Tribune'
  if (source == "NYT-Let") name <- 'New York Times'
  if (source == "RevReviews") name <- 'Review of Reviews'
  if (source == "Century") name <- 'Century'
  if (source == "NorthAmRev") name <- 'North American Review'
  if (source == "SouthAtlanticQ") name <- 'South Atlantic Quarterly'
  if (source == "GoodHouse") name <- 'Good Housekeeping'
  if (source == "Scribners") name <- 'Scribners'
  if (source == "Independent") name <- 'Independent'
  if (source == "NatGeog") name <- 'National Geographic'
  if (source == "AmerMag") name <- 'American Magazine'
  if (source == "YaleRev") name <- 'Yale Review'
  return(name)
}

instance.table$DocId <- NA 
instance.table$MatchTitle <- NA 
instance.table$MatchFullSource <- NA 
for (i in 1:dim(instance.table)[1]) {
  if (i %% 100 == 0) print(i)
  genre <- instance.table[i, 'Genre']
  source <- instance.table[i, 'Source']
  source_year <- instance.table[i, 'Year']
  source_text <- instance.table[i, 'concordance']
  
  if (genre %in% c('MAG', 'NEWS')) {
    DocList <- find_mag_docid(source=source, source_year=source_year, source_text, metadata=metadata)
  } else {
    DocList <- find_nonmag_docid(source=source, source_year=source_year, metadata=metadata)
  }
  
  instance.table[i, 'DocId'] <- DocList$DocId
  instance.table[i, 'MatchTitle'] <- DocList$Title
  instance.table[i, 'MatchFullSource'] <- DocList$FullSource
}

# 4. Save --------------------
write.csv(instance.table, file.path('outputs', 'instance_table.csv'), row.names=FALSE)
