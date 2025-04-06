import google.generativeai as genai

genai.configure(api_key="AIzaSyD5Sbjmn0YYVnbWTtopTi42IpYUATU8PIc")

models = genai.list_models()
for model in models:
    print(model.name)
