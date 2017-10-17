# lambda-kms-watcher

Lambda python2.7 function to watch any changes from AWS DynamoDB Changes stream and trigger an event to salt-api for service orchestrtation.


## Requirements

Python modules `json`, `re` and `botocore.vendored`.


## Watch specific table ID 

There is a very basic filtering based on regex to watch a specific changes on a Table ID. 
However we should improve that given that we can't have more than 2 watcher on the same Dynamo shards. 

Eventually we should have some kind of changes router in front of this lambda, to forward event to different APIs; particularily useful if multiple places consummed the same DynamoDB table.


## salt-api authentication

The authentication with `salt-api` must be made with `PAM` on `/login` endpoint and then return the `token` received.

Update the credentials in the script:

```
url = 'https://salt-api:8000'
user = 'USER'
password = 'PASS'
```


## salt-api webhook

You can customize the event sent by creating any other function, or updating the `trigger` one.

Event example for an scaling up event:

```
def scale_up():
    """Trigger salt-api call."""
    data = {'instances': '2', 'service': 'web'}
    return request('/hook/scale_up', data=data)
```

You can now setup salt-reactor to trigger any actions you need.
