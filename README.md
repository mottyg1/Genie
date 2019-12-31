# Genie - Query Templates Made Easier
Genie is a jinja2 "supplement" which helps you generate queries from
 HTML forms or JSON objects easily, while retaining full control over the 
 query's structure.
 > "Let's make some magic!"
 > 
 > ~ Genie, Aladdin

# Getting Started
We'll start with a simple example.
Let's say we have the following JSON which represents a
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

### Query Types
As you can see, in the elasticsearch template the names string array 
turned by default into a _terms_ clause. What if we want it to be a _match_ clause?
We can apply a __match__ filter on the name field:
```
{{ name|match }}
```
Which will render into this clause:
```json
{
  "bool": {
    "should": [
      {
        "match": {
          "name": {
            "value": "Toy Story"
          }
        }
      },
      {
        "match": {
          "name": {
            "value": "Lion King"
          }
        }
      }
    ]
  }
}
```
There are many builtin types of filters genie comes with. You can find their list in the reference.

To learn how those filters work and how you can write your own look at the developer docs.
### Missing Values
Staying with our example, what happens if the json is missing some key that is defined in the template?

Looking at the above examples lets say we are only filtering on name but not on year.
Our input JSON will look like this:
```json
{
 "name": ["Toy Story", "Lion King"]
}
```
If we leave the the same templates as before our rendered queries will look like this:
```json
{
  "query": {
    "bool": {
      "must": [
        { "terms": { "name": ["Toy Story", "Lion King"] } },
      ]
    }
  }
}
```
and for the solr version:

```
name: ("Toy Story" "Lion King") AND
```

This is very bad because those queries are malformed and will throw an exception on execution.
We can make our template smarter using jinjas conditional but that would be trouble.

Genie comes with two great and useful filters called __dirty_json__ and __dirty_solr__.
Updating our templates as follows will do the work:
```
{% set genie = namespace(dialect="elasticsearch") %}
{% filter dirty_json %}
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
{% endfilter %}
```
```
{% set genie = namespace(dialect="solr") %}
{% filter dirty_solr %}
{{ name }} AND {{ year }}
{% endfilter %}
```
After rendering they will produce valid queries:
```json
{
  "query": {
    "bool": {
      "must": [
        { "terms": { "name": ["Toy Story", "Lion King"] } }
      ]
    }
  }
}
```
```
name: ("Toy Story" "Lion King")
```

Notice though that those filter will only correct queries that are invalid because of missing keys.
Other malformations should be handled by the template designer.
To learn how those filters work, reference the developer docs.

### Dialect
The active dialect in a template is whats used to evaluate the format of the different clauses.
The default dialect is None which evaluates expressions like regular jinja2 names.
You can set and change the dialect wherever you want inside the template using jinja2 set block:
```
{% set genie = namespace(dialect="elasticsearch") %}
```
After the first declaration you can change it like that:
```
{% set genie.dialect = "solr" %}
```
or to disable the dialect:
```
{% set genie.dialect = None %}
```
This powerful mechanism allows you to create templates with multiple dialects.
For example elasticsearch DSL with a lucene _query_string_ filter or SQL with inner elasticseach DSL queries.

Currently the available dialects are:  
- solr
- elasticsearch

See the reference for more.

### Default Evaluations
Unless a specific query type was applied, Genie attaches to each evaluated 
key a default query type based on the active dialect in the template.
In the elasticsearch dialect for example, _strings_, _integers_ and _lists_ evaluate into term and terms 
queries while _objects_ that have a _from_ and _to_ keys evaluate into range queries.
You can find a list of all the defaults behaviors in the reference.


# Reference
List of available filters in each dialect

### Global Filters
- __key__ - change the key the expression is filtering on. Usage:
    ```
    {{ name|key('first_name') }} OR {{ name|key('last_name') }}
    ```
    This template will filter both on first_name and on last_name
- __raw__ - the expression will evaluate in it raw value disregarding the configured dialect 
(quicker than disabling and enabling the dialect again) 

### ElasticSearch Filters
- __match__ - changes the query type to match instead of term. Works on strings and lists.

### Solr Filters
- Nothing to find here for now

# WIP - Developer Documentation
> "Like so many things, it is not what's outside, but what is inside that counts."
> 
> ~ Merchant, Aladdin

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