#!/bin/bash

# Change ownership of following directories to allow write rights for developer user
sudo chown -R developer:odoo /var/lib/odoo /var/log/odoo
sudo chmod -R 775 /var/lib/odoo /var/log/odoo

# # Create symbolic link odoo-sources pointing to odoo sources in docker image.
# # ATTENTION: Like this the link is created under root user.
# # To create it under developer user (= local user) use "postStartCommand" in devcontainer.json
# sudo rm -f /mnt/odoo-sources
# sudo ln -s /usr/lib/python3/dist-packages/odoo /mnt/odoo-sources

# # The official image entrypoint.sh is ommited as it starts odoo in background and we would like to start it manually.
# # If ever you would like to launch it you can uncomment following code (and remove the `exec "$@"` here below):
#     # Execute the original entrypoint script
#     exec /entrypoint.sh "$@"

exec "$@"