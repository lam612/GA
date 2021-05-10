import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config
import pickle

market_demand = config.market_demand
model_filename = "demand_model.sav"

df = pd.DataFrame(market_demand, columns=[
                  'month', 'manu_discount', 'retailer_discount', 'sell_price', 'demand'])
X = df[['manu_discount', 'retailer_discount', 'sell_price']].astype(float)
Y = df['demand'].astype(float)


def build_model():
    # Sklearn
    model = linear_model.LinearRegression()
    model.fit(X, Y)
    pickle.dump(model, open(model_filename, 'wb'))
    return model


def get_model():
    try:
        demand_model = pickle.load(open(model_filename, 'rb'))
    except:
        demand_model = build_model()
    print(demand_model)
    return demand_model


def get_predict_demand(model, manu_discount, retailer_discount, sell_price):
    prediction_result = model.predict(
        [[manu_discount, retailer_discount, sell_price]])
    return prediction_result
