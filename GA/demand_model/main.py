from predict_demand_model import PredictDemandModel


def get_predict_value(coef, intercept, manu_discount, retailer_discount, sell_price):
    return manu_discount * coef[0] + retailer_discount * coef[1] + sell_price * coef[2] + intercept


manu_discount, retailer_discount, sell_price = 100, 100, 1.700
demand_model = PredictDemandModel()
model_val = demand_model.get_model_val(rebuild_model=1)
predict_demand = get_predict_value(model_val['coef'], model_val['intercept'],
                                   manu_discount, retailer_discount, sell_price)
print('[+] Predict product demand : {}'.format(predict_demand))
