# Simple App (FastAPI + Mongo) 

## Run
```bash
cd simple-mongo-app
docker compose up -d --build
curl http://127.0.0.1:8000/health
curl -i -s -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name":"hello"}'
curl -s http://127.0.0.1:8000/items
```

## Troubleshooting
```bash
docker compose logs --tail=200 app
```
