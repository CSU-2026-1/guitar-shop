import consul
import socket
import logging
import os

logger = logging.getLogger(__name__)

class ConsulConfig:
    def __init__(self, service_name, service_port, health_path="/health"):
        self.consul_host = os.getenv("CONSUL_HOST", "consul")
        self.consul_port = int(os.getenv("CONSUL_PORT", 8500))
        self.service_name = service_name
        self.service_port = service_port
        self.health_path = health_path
        self.instance_id = f"{service_name}-{socket.gethostname()}"
        self.c = consul.Consul(host=self.consul_host, port=self.consul_port)

    def register(self):
        try:
            # Получаем IP адрес контейнера внутри сети Docker
            ip_address = socket.gethostbyname(socket.gethostname())
            
            self.c.agent.service.register(
                name=self.service_name,
                service_id=self.instance_id,
                address=ip_address,
                port=self.service_port,
                check={
                    "http": f"http://{ip_address}:{self.service_port}{self.health_path}",
                    "interval": "10s",
                    "timeout": "5s",
                    "deregister_critical_service_after": "1m"
                }
            )
            logger.info(f"Registered service {self.service_name} with ID {self.instance_id}")
        except Exception as e:
            logger.error(f"Failed to register service in Consul: {e}")

    def deregister(self):
        try:
            self.c.agent.service.deregister(self.instance_id)
            logger.info(f"Deregistered service {self.instance_id}")
        except Exception as e:
            logger.error(f"Failed to deregister service from Consul: {e}")
