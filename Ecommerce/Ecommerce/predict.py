import numpy as np
import pandas as pd
from sklearn.externals import joblib 
import warnings
warnings.filterwarnings("ignore")

#model = joblib.load('./ecommerce/tsecmodel.pkl') 
#vec = joblib.load('./ecommerce/tsecvectorizer.pickle')
#df = pd.read_csv('./ecommerce/updateddata.csv')
def predict(i):
    df2 = pd.DataFrame({"A": [i]})
    apnatesting = vec.transform(df2['A'])
    X_test_1 = apnatesting.toarray()
    pred = model.predict(X_test_1)[0]
    df3 = df[df['category_class'] == pred]
    cat = list(df3.category)[0]
    return cat


