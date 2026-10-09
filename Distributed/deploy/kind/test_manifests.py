"""Manifest checks for the kind packaging. They do not start a cluster."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

POSTGRES_SERVICES = {"order-postgres", "reporting-postgres", "notification-postgres", "odoo-postgres"}
DATA_SERVICES = POSTGRES_SERVICES | {"redis", "rabbitmq"}


def documents(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip() == "---":
            parts.append("\n".join(buf))
            buf = []
        else:
            buf.append(line)
    parts.append("\n".join(buf))
    return [part for part in parts if part.strip()]


def kind_of(doc: str) -> str:
    match = re.search(r"^kind:\s*(\S+)", doc, re.M)
    return match.group(1) if match else ""


def metadata_name(doc: str) -> str:
    match = re.search(r"^  name:\s*(\S+)", doc, re.M)
    return match.group(1) if match else ""


def spec_type(doc: str) -> str:
    match = re.search(r"^  type:\s*(\S+)", doc, re.M)
    return match.group(1) if match else ""


class KindManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = {
            path.name: path.read_text(encoding="utf-8")
            for path in ROOT.iterdir()
            if path.suffix in {".yaml", ".yml"}
        }
        cls.docs = []
        for name, text in cls.files.items():
            for doc in documents(text):
                cls.docs.append((name, doc))

    def test_postgres_services_are_not_published(self) -> None:
        found = set()
        for name, doc in self.docs:
            if kind_of(doc) != "Service":
                continue
            service = metadata_name(doc)
            published = spec_type(doc) in {"NodePort", "LoadBalancer"}
            if service in DATA_SERVICES or re.search(r"port:\s*5432\b", doc):
                self.assertFalse(published, f"{name} publishes {service} as {spec_type(doc)}")
                if service in DATA_SERVICES:
                    found.add(service)
                    self.assertNotIn("nodePort:", doc)
        self.assertEqual(found, DATA_SERVICES)

    def test_ingress_does_not_publish_internal_or_data_stores(self) -> None:
        ingresses = [doc for _, doc in self.docs if kind_of(doc) == "Ingress"]
        self.assertEqual(len(ingresses), 1)
        ingress = ingresses[0]
        self.assertNotIn("/api/v1/internal", ingress)
        self.assertIn("name: gateway", ingress)
        for blocked in ("order-postgres", "reporting-postgres", "notification-postgres", "odoo-postgres", "redis", "rabbitmq"):
            self.assertNotIn(f"name: {blocked}", ingress)

    def deployment(self, name: str) -> str:
        matches = [
            doc
            for _, doc in self.docs
            if kind_of(doc) == "Deployment" and metadata_name(doc) == name
        ]
        self.assertEqual(len(matches), 1, name)
        return matches[0]

    def test_order_service_hpa_and_competing_consumers(self) -> None:
        cronjobs = [doc for _, doc in self.docs if kind_of(doc) == "CronJob"]
        self.assertEqual([metadata_name(doc) for doc in cronjobs], ["order-retention"])
        hpas = [doc for _, doc in self.docs if kind_of(doc) == "HorizontalPodAutoscaler"]
        self.assertEqual(len(hpas), 1)
        hpa = hpas[0]
        self.assertEqual(metadata_name(hpa), "order-service")
        self.assertIn("kind: Deployment", hpa)
        self.assertIn("name: order-service", hpa)
        self.assertIn("averageUtilization: 70", hpa)
        minimum = int(re.search(r"^  minReplicas:\s*(\d+)\s*$", hpa, re.M).group(1))
        maximum = int(re.search(r"^  maxReplicas:\s*(\d+)\s*$", hpa, re.M).group(1))
        self.assertGreaterEqual(minimum, 2)
        self.assertGreater(maximum, minimum)
        order = self.deployment("order-service")
        self.assertGreaterEqual(int(re.search(r"^  replicas:\s*(\d+)\s*$", order, re.M).group(1)), 2)
        self.assertIn("cpu: 100m", order)
        inventory = self.deployment("order-inventory-consumer")
        self.assertGreaterEqual(int(re.search(r"^  replicas:\s*(\d+)\s*$", inventory, re.M).group(1)), 2)
        reporting = self.deployment("reporting-consumer")
        self.assertGreaterEqual(int(re.search(r"^  replicas:\s*(\d+)\s*$", reporting, re.M).group(1)), 2)
        publisher = self.deployment("order-outbox-publisher")
        self.assertEqual(int(re.search(r"^  replicas:\s*(\d+)\s*$", publisher, re.M).group(1)), 1)
        ingresses = [doc for _, doc in self.docs if kind_of(doc) == "Ingress"]
        self.assertEqual(len(ingresses), 1)
        self.assertNotIn("/api/v1/internal", ingresses[0])
        self.assertIn("--kubelet-insecure-tls", self.files["metrics-server.yaml"])

    def test_order_service_readiness_replicas_and_hpa_bounds(self) -> None:
        order = self.deployment("order-service")
        self.assertEqual(int(re.search(r"^  replicas:\s*(\d+)\s*$", order, re.M).group(1)), 2)
        self.assertIn("terminationGracePeriodSeconds: 20", order)
        self.assertIn("path: /health/ready", order)
        self.assertNotIn("sessionAffinity:", order)
        services = [
            doc
            for _, doc in self.docs
            if kind_of(doc) == "Service" and metadata_name(doc) == "order-service"
        ]
        self.assertEqual(len(services), 1)
        self.assertIn("type: ClusterIP", services[0])
        self.assertNotIn("sessionAffinity:", services[0])
        hpas = [doc for _, doc in self.docs if kind_of(doc) == "HorizontalPodAutoscaler"]
        self.assertEqual(len(hpas), 1)
        hpa = hpas[0]
        self.assertEqual(int(re.search(r"^  minReplicas:\s*(\d+)\s*$", hpa, re.M).group(1)), 2)
        self.assertEqual(int(re.search(r"^  maxReplicas:\s*(\d+)\s*$", hpa, re.M).group(1)), 4)
        self.assertIn("name: cpu", hpa)
        self.assertIn("averageUtilization: 70", hpa)

    def test_retention_cronjob_is_bounded_and_uses_order_db(self) -> None:
        cronjobs = [doc for _, doc in self.docs if kind_of(doc) == "CronJob"]
        self.assertEqual(len(cronjobs), 1)
        cron = cronjobs[0]
        self.assertEqual(metadata_name(cron), "order-retention")
        self.assertIn("namespace: commerce", cron)
        self.assertIn('schedule: "30 3 * * *"', cron)
        self.assertIn("concurrencyPolicy: Forbid", cron)
        self.assertIn("startingDeadlineSeconds: 3600", cron)
        self.assertIn("activeDeadlineSeconds: 600", cron)
        self.assertIn("restartPolicy: OnFailure", cron)
        self.assertIn(
            'command: ["python", "-m", "order_service.infrastructure.database.retention"]',
            cron,
        )
        self.assertNotIn("sh -c", cron)
        self.assertIn("@order-postgres:5432/order_db", cron)
        self.assertNotIn("reporting_db", cron)
        self.assertNotIn("odoo_db", cron)
        self.assertNotIn("BEGIN PRIVATE KEY", cron)
        self.assertIn("- retention.yaml", self.files["kustomization.yaml"])
        self.assertNotIn("Job", {kind_of(doc) for _, doc in self.docs})

    def test_database_hosts_are_service_names(self) -> None:
        joined = "\n".join(self.files.values())
        self.assertIn("@order-postgres:5432/order_db", joined)
        self.assertIn("@reporting-postgres:5432/reporting_db", joined)
        self.assertIn("@notification-postgres:5432/notification_db", joined)
        self.assertIn("@odoo-postgres:5432/odoo_db", joined)
        self.assertIn("@rabbitmq:5672/", joined)
        self.assertIn("redis://redis:6379/0", joined)
        self.assertNotIn("@localhost", joined)
        self.assertNotIn("@127.0.0.1", joined)
        self.assertNotIn("@postgres:", joined)

    def test_example_secret_has_no_private_key_or_filled_token(self) -> None:
        example = self.files["secrets.example.yaml"]
        self.assertNotIn("BEGIN PRIVATE KEY", example)
        self.assertNotIn("BEGIN RSA PRIVATE KEY", example)
        self.assertIn('INTERNAL_SERVICE_TOKEN: ""', example)
        kustomization = self.files["kustomization.yaml"]
        self.assertNotIn("secrets.example.yaml", kustomization)

    def test_apply_script_loads_images_and_does_not_delete_a_cluster(self) -> None:
        script = (ROOT / "apply.sh").read_text(encoding="utf-8")
        self.assertIn("kind create cluster --config deploy/kind/kind-config.yaml", script)
        self.assertIn("kind load docker-image", script)
        self.assertIn("deploy/compose/dynamic.yaml", script)
        self.assertIn("deploy/observability/prometheus/prometheus.yml", script)
        self.assertNotIn("kind delete", script)
        self.assertNotIn("secrets.example.yaml", script)
        self.assertNotIn(":latest", "\n".join(self.files.values()))

    def test_redis_has_no_volume_claim(self) -> None:
        self.assertNotIn("PersistentVolumeClaim", self.files["redis.yaml"])
        self.assertIn("cache", self.files["redis.yaml"].lower())


if __name__ == "__main__":
    unittest.main()
