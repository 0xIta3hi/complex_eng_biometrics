echo "[+] Starting the server's"
python -m src.party --party-id 0 --port 8001 & python -m src.party --party-id 1 --port 8002 & python -m src.party --party-id 2 --port 8003
echo "[+] Server's started"

echo "[+] running the demo script"
python -m src.demo