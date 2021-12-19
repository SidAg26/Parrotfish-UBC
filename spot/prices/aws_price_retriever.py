from spot.prices.price_retriever import PriceRetriever
import os
import json
import time as time
from spot.db.db import DBClient


class AWSPriceRetriever(PriceRetriever):
    
    def __init__(self, url, port):
        super().__init__()
        self.DBClient = DBClient(url, port) 

        

    def fetch_current_pricing(self, region="us-east-1") -> dict:
        current_pricing = {}
       
        parameters = {"vendor": "aws", "service": "AWSLambda", "family": "Serverless", "region": region, "type": "AWS-Lambda-Requests", "purchaseOption": "on_demand"}
        request_price = self._current_price(parameters)
        current_pricing["request_price"] = request_price
        parameters["type"] = "AWS-Lambda-Duration"
        duration_price = self._current_price(parameters)
        current_pricing["duration_price"] = duration_price
        current_pricing["timestamp"] = int(time.time()*100)
        current_pricing["region"] = region

        self.DBClient.add_document_to_collection_if_not_exists("pricing", "AWS", current_pricing, {"request_price" : request_price, "duration_price": duration_price, "region" : region})
        
        return current_pricing

'''
a = AWSPriceRetriever("localhost", 27017)
a.fetch_current_pricing()
'''