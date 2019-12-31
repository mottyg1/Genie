# Genie
Genie is a jinja2 "supplement" which helps you generate queries from
 HTML forms or json object easily, while retaining full control over the 
 query's structure.
 > _"Let's make some magic!"_ ~ Genie

# Getting Started
We'll start with a simple elasticsearch example.
Let's say we have the following json which represents a
 query on some movies table where
  the name of the movie is "Toy Story" or "Lion King" 
  and the movie was out between 2005 to 2019
```json
{
 "name": ["Toy Story", "Lion King"],
 "year": {
  "from": "2005",
  "to": "2019"
 }
}
```
We can then define the following elasticsearch query template:
```
{% set genie = namespace(dialect="elasticsearch") %}
{
  "query": {
    "bool": {
      "must": [
        {{ name }},
        {{ year }}
      ]
    }
  }
}

```
or the following Solr (lucene) template:
```
{% set genie = namespace(dialect="solr") %}
{{ name }} AND {{ year }}
```
Rendering any of them using genie:
```python
from genie.environment import GenieEnvironment

query = GenieEnvironment().from_string(template).render(json)
```
will result in the following queries respectively:
```json
{
  "query": {
    "bool": {
      "must": [
        { "terms": { "name": ["Toy Story", "Lion King"] } },
        { "range": { "year": { "gt": "2005", "lt": "2019" } } }
      ]
    }
  }
}
```
or
```
name: ("Toy Story" "Lion King") AND year: [2005 TO 2019]
```
which are both fully valid and runnable right out of the box!

## query types

## missing values

## default evaluations

## dialect
- solr
- elasticsearch
##### TBD
- oracle
- impala
- sql server

# Reference
filters in each dialect
## global

## elastic

## solr

# Developer Documentation
### Intro
jinja2 features in use

### The Expression Object

### types of filters

### representation functions

### dialect
- finalize
- genie name space
 
### dirty filters
- json
- solr lucene