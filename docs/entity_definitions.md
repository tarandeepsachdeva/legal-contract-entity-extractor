# Named Entity Definitions – Legal Contract NER

## Overview
This document defines the entity labels used for Named Entity Recognition (NER) in legal contracts. These entities were selected based on common information required from contractual documents.

---

## Entity List

| Entity Name | Label | Description |
|------------|------|-------------|
| Party Name | PARTY | Companies or individuals involved in the contract |
| Date | DATE | Any legal or contractual date |
| Effective Date | EFFECTIVE_DATE | The date on which the agreement becomes legally effective
| Term Duration | TERM_DURATION | The length of time for which the agreement remains valid
| Amount | AMOUNT | Monetary values mentioned in the contract |
| Location | LOCATION | Addresses, cities, or legal locations |
| Agreement Type | AGREEMENT_TYPE | Type or title of the legal agreement |

---

## Annotation Guidelines

### PARTY
**Definition:**  
Names of organizations or individuals entering into the contract.

**Include:**  
- Company names  
- Individual names  

**Exclude:**  
- Job titles alone (e.g., Director)

**Example:**  
This Agreement is between [Air Industries Group Inc]PARTY and [John Smith]PARTY

---

### DATE
**Definition:**  
Dates related to execution, signing, or validity of the agreement.

**Include:**  
- Full dates  
- Partial dates (month/year)

**Example:**  
dated as of [December 31, 2008]DATE

---

### EFFECTIVE_DATE

**Definition:**
The date on which the agreement becomes legally effective or comes into force.

**Include:**
Dates explicitly referred to as effective date
Phrases like “effective as of”, “commencing on”

**Example:**
This Agreement shall be effective as of [January 1, 2023]EFFECTIVE_DATE

---

### TERM_DURATION
**Definition:**
The length of time for which the agreement remains valid.

**Include:**
Durations such as years, months, or days
Phrases like “for a period of”, “term of this agreement”

**Example:**
This Agreement shall remain in effect for a period of [five (5) years]TERM_DURATION

--- 
### AMOUNT
**Definition:**  
Any monetary value mentioned in the document.

**Include:**  
- Currency symbols with numbers  
- Comma-separated values

**Example:**  
purchase price of [$500,000]AMOUNT

---

### LOCATION
**Definition:**  
Geographical locations and addresses.

**Include:**  
- City names  
- States, countries  
- Full addresses

**Example:**  
located at [New York]LOCATION

---

### AGREEMENT_TYPE
**Definition:**  
The title or type of legal agreement.

**Include:**  
- Contract titles appearing in headings

**Example:**  
[STOCK PURCHASE AGREEMENT]AGREEMENT_TYPE

---

