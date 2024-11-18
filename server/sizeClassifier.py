import pickle
import pandas as pd



def classifySize(chest_size,shirt_size,shoulder_len,brand):

    x = [[chest_size,shirt_size,shoulder_len]]

    with open('files/rf.pkl', 'rb') as file:
        rf = pickle.load(file)
    with open('files/gb.pkl', 'rb') as file:
        gb = pickle.load(file)
    with open('files/svr.pkl', 'rb') as file:
        svr = pickle.load(file)
    with open('files/model.pkl', 'rb') as file:
        model = pickle.load(file)

    with open('files/scaler.pkl', 'rb') as file:
        scale = pickle.load(file)

    res1 = rf.predict(x)
    res2 = gb.predict(x)
    res3 = svr.predict(scale.transform(x))
    x_test_stack = pd.DataFrame({'Random Forest': res1, 'Gradient Boosting': res2, 'SVR': res3})

    res = model.predict(x_test_stack)
    s = round(res[0],2)
    print(s)
    df = pd.read_csv("files/sizes.csv")
    df1 = df.loc[df['Brand Name'] == brand]
    print(df1)
    recommended_size = ""
    i = 0
    for index, row in df1.iterrows():
        if(i<df1.shape[0]-1):
            if(i==0 and s<=df1["Size"][index]):
                recommended_size = df1["Brand Size"][index]
                break
            elif(s>df1["Size"][index] and s<=df1["Size"][index+1]):
                recommended_size = df1["Brand Size"][index+1]
                break
        else:
            recommended_size = df1["Brand Size"][index]
            break
        i+=1
        print("recommended_size:"+recommended_size)
    return recommended_size

