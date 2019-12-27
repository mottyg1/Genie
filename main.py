from genie.environment import GenieEnvironment
import yaml
from luqum.parser import parser as luqum_parser
from luqum.pretty import prettify as luqum_prettify

props = {
  #  "index": "all_data",
    "name": ["mot", "yos", "itt"],
    "start_time": {
        "from": "2019-01-01T07:00:00.000Z",
        "to": "2020-01-01T07:00:00.000Z"
    }
}

env = GenieEnvironment('/home/mottyg/ws/Genie/examples')

# result = env.render('elasticsearch.yaml', props)
result = env.render('solr.yaml', props)
query = yaml.full_load(result)['execution']['json']['fq']
print(query)
print()
tree = luqum_parser.parse(query)
print(luqum_prettify(tree))



