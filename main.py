from genie.environment import GenieEnvironment

props = {
    "index": "all_data",
    "name": ["mot", "yos", "itt"],
    "start_time": {
        "from": "2019-01-01 07:00:00.000",
        "to": "2020-01-01 07:00:00.000"
    }
}

env = GenieEnvironment('/home/mottyg/ws/Genie/examples')

result = env.render('elasticsearch.yaml', props)
print(result)
