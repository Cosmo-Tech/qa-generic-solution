import os

for k in os.environ.keys():
    if k in ["username", "password", "CSM_API_KEY"]:
        print(k)
        print(f"--> {os.environ[k]}")
