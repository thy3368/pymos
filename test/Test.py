
from vanna.remote import VannaDefault
vn = VannaDefault(model='chinook', api_key='e5dadc3ac9b144f38a02126dd6352676')
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
vn.ask('What are the top 10 artists by sales?')

from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run()