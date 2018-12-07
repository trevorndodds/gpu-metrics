# gpu-metrics

https://grafana.com/dashboards/7320

Build and run Docker Container:
```bash
docker build -t <user>/gpu-elastic-metrics:latest .
```

To run it:
```bash
docker run -t -d --runtime=nvidia --restart always --name cuda-gpu-metrics \ 
-e GPU_METRICS_CLUSTER_URL='http://elasticURL:9200' <user>/gpu-elastic-metrics:latest 
```

Alternative: Create Systemd service

Create Folder and copy webhook:
```bash
sudo mkdir -p /data/scripts/gpu/
sudo cp /tmp/gpu_elastic.py /data/scripts/gpu/
```
Create Service
```bash
sudo vi /etc/systemd/system/gpu_elastic.service
```
Copy the below in the service file:
```bash
[Unit]
Description=GPU Metric Service
After=multi-user.target

[Service]
Environment=PYTHONUNBUFFERED=true
Type=simple
ExecStart=/data/scripts/gpu/gpu_elastic.py
User=root
WorkingDirectory=/data/scripts/gpu
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Execute:
```bash
sudo chmod 664 /etc/systemd/system/gpu_elastic.service
sudo chmod +x /data/scripts/gpu/gpu_elastic.py
```
Register and Start the Service:
```bash
sudo systemctl enable gpu_elastic.service 
sudo systemctl daemon-reload
sudo systemctl start gpu_elastic.service
```
To View Status and logs execute:
```bash
sudo systemctl status gpu_elastic.service -l
sudo journalctl -u gpu_elastic.service -xn -l
sudo journalctl -u gpu_elastic.service
```
