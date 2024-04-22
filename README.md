# Glazer EZE API connections Package
# Developed by Carolyn Chen & Cem Civelek

### 
To install via SSH:
`pip install git+ssh://git@github.com/Glazer-Capital/Glazer_EZEManager.git`

### Sample code

```
from GLAZER_EZE_REST.glazer_eze_rest_api import EZEManager

eze_manager = EZEManager()
columns = ['Alias2', 'PosAction', 'FilledAmt', 'TradeAvgPrice', 'TradeDateAPI']
df, response, error = eze_manager.get_analytics(endpoint='Active Trades API', columns=columns)
```
