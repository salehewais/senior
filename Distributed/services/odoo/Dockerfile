# Odoo 18 Community plus commerce_connector and the worker package.
# The HTTP process, the OrderConfirmed consumer, and the inventory publisher
# use this image with different commands. Tokens are not copied into a layer.
FROM odoo:18.0

USER root

RUN if ! command -v pip3 >/dev/null 2>&1; then \
      apt-get update \
      && apt-get install -y --no-install-recommends python3-pip \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && pip3 install --no-cache-dir --break-system-packages "pika>=1.3,<2" "psycopg[binary]>=3.2"

COPY addons /mnt/extra-addons
COPY src /opt/commerce_erp_src

# odoo.conf is mounted at runtime. It is not copied into this image.
RUN chown -R odoo:odoo /mnt/extra-addons /opt/commerce_erp_src

ENV PYTHONPATH=/opt/commerce_erp_src

USER odoo
