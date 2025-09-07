
from pydantic import BaseModel
from typing import List
class SalesData(BaseModel):
    date:str; currency:str='INR'; total_sales:float; new_customers:int; orders:int; avg_order_value:float
class Campaign(BaseModel):
    name:str; click_rate:float=0.0; conversions:int=0; spend:float=0.0; revenue:float=0.0
class MarketingData(BaseModel):
    date:str; campaigns:List[Campaign]
