# DNS Resolver

## Table of Contents
- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [Features](#features)
- [How It Works](#how-it-works)
- [Additional Notes](#additional-notes)
- [Contribution and Modification](#contribution-and-modification)
- [Credits](#credits)

## Overview

The `resolve.py` script represents a sophisticated recursive DNS resolver leveraging the capabilities of the `dnspython` library. This implementation stands out due to several notable features and strengths:

### Comprehensive DNS Record Retrieval

The script excels in fetching a wide range of DNS records associated with domain names, including "A", "AAAA", "MX", and "CNAME" records. Its ability to gather diverse records provides a comprehensive snapshot of a domain's DNS configuration.

### Robust Error Handling

One of its standout qualities is its robustness in handling potential errors encountered during DNS resolution. It employs a timeout mechanism of 3 seconds for queries, efficiently managing unresponsive or slow DNS servers. Additionally, the script exhaustively tries all available servers, ensuring a thorough attempt at resolving queries before signaling a failure.

### Efficient Caching System

A notable feature is its implementation of a caching mechanism. This system intelligently stores previously resolved DNS queries, eliminating redundant queries for previously accessed domain information. This optimization not only enhances performance but also minimizes the load on DNS servers.

## Setup
Before running the script, ensure you have the `dnspython` library installed. You can install it using pip:
``` pip install dnspython ```

## Usage
Execute the script from the command line, providing one or multiple domain names as arguments:
```python resolve.py example.com google.com```

## Features
- **DNS Record Lookups**: Retrieves "A", "AAAA", "MX", and "CNAME" records for the specified domain names.
- **Error Handling**: Handles unresponsive or slow DNS servers using a timeout value of 3 seconds for queries. It exhaustively tries all available servers before giving up.
- **Caching System**: Implements a caching system to store previously resolved DNS queries, reducing redundant queries for the same domain.
- **IPv4 Only**: Performs queries exclusively over IPv4 and avoids querying over IPv6 for domain resolution.

## How It Works
The script initiates queries by contacting a root server (IP addresses are hardcoded in `ROOT_SERVERS`). It executes recursive DNS lookups by navigating through the DNS hierarchy to resolve the requested domain name. It adeptly handles different record types and aliases.

## Additional Notes
- The `collect_results` function parses final answers into the required data structure for displaying comprehensive DNS information.
- Variables like `cache` and `intermediate_cache` store resolved results to optimize subsequent queries and reduce the load on DNS servers.
- The resolver efficiently manages CNAME restarts, unglued nameservers, and avoids throwing exceptions, presenting a summary of DNS information for the specified domain names.

## Credits
This resolver script utilizes the `dnspython` library and has been developed as part of an assignment or project for [course name/assignment description].
