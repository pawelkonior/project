


## add description for cert:
```bash

 uvicorn "main:app" --host 0.0.0.0 --port 8000 --ssl-keyfile=./.cert/key.pem --ssl-certfile=./.cert/cert.pem --reload


```