#!/bin/bash
# Set up a Frappe/ERPNext version-16 bench and install erpnextswiss into a test
# site. Mirrors the official frappe app CI helper (frappe/payments) and adds the
# `hrms` app: erpnextswiss has doctypes that Link to Employee / Salary Slip /
# Expense Claim / Salary Component, and Frappe's CI-mode DocType validation
# (triggered by the CI env var) requires those link targets to exist.

set -e

cd ~ || exit

sudo apt update
sudo apt remove -y mysql-server mysql-client || true
sudo apt install -y libcups2-dev redis-server mariadb-client

pip install frappe-bench

githubbranch=${GITHUB_BASE_REF:-${GITHUB_REF##*/}}
frappeuser=${FRAPPE_USER:-"frappe"}
frappebranch=${FRAPPE_BRANCH:-$githubbranch}
erpnextbranch=${ERPNEXT_BRANCH:-$githubbranch}
hrmsbranch=${HRMS_BRANCH:-$githubbranch}

git clone "https://github.com/${frappeuser}/frappe" --branch "${frappebranch}" --depth 1
bench init --skip-assets --frappe-path ~/frappe --python "$(which python)" frappe-bench

mkdir ~/frappe-bench/sites/test_site
cp -r "${GITHUB_WORKSPACE}/.github/helper/site_config.json" ~/frappe-bench/sites/test_site/

mariadb --host 127.0.0.1 --port 3306 -u root -proot -e "SET GLOBAL character_set_server = 'utf8mb4'"
mariadb --host 127.0.0.1 --port 3306 -u root -proot -e "SET GLOBAL collation_server = 'utf8mb4_unicode_ci'"

mariadb --host 127.0.0.1 --port 3306 -u root -proot -e "CREATE USER 'test_frappe'@'localhost' IDENTIFIED BY 'test_frappe'"
mariadb --host 127.0.0.1 --port 3306 -u root -proot -e "CREATE DATABASE test_frappe"
mariadb --host 127.0.0.1 --port 3306 -u root -proot -e "GRANT ALL PRIVILEGES ON \`test_frappe\`.* TO 'test_frappe'@'localhost'"

mariadb --host 127.0.0.1 --port 3306 -u root -proot -e "FLUSH PRIVILEGES"

install_wkhtmltopdf() {
    wget -q -O /tmp/wkhtmltox.tar.xz https://github.com/frappe/wkhtmltopdf/raw/master/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
    tar -xf /tmp/wkhtmltox.tar.xz -C /tmp
    sudo mv /tmp/wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf
    sudo chmod o+x /usr/local/bin/wkhtmltopdf
}
install_wkhtmltopdf &

cd ~/frappe-bench || exit

sed -i 's/watch:/# watch:/g' Procfile
sed -i 's/schedule:/# schedule:/g' Procfile
sed -i 's/socketio:/# socketio:/g' Procfile
sed -i 's/redis_socketio:/# redis_socketio:/g' Procfile

bench get-app "https://github.com/${frappeuser}/erpnext" --branch "$erpnextbranch" --resolve-deps
bench get-app "https://github.com/frappe/hrms" --branch "$hrmsbranch" --resolve-deps
# Install the app under test from the checkout. This runs
# `uv pip install -e apps/erpnextswiss`, exercising the pyproject.toml packaging.
bench get-app erpnextswiss "${GITHUB_WORKSPACE}"

bench setup requirements --dev

bench start &>> ~/frappe-bench/bench_start.log &
CI=Yes bench build --app frappe &

# reinstall creates the DB schema and installs the apps from site_config
# install_apps (erpnext, hrms, erpnextswiss) in order.
bench --site test_site reinstall --yes

# Explicit install-app (no-op if reinstall already installed it) so the exact
# command from the task's acceptance criteria is exercised.
bench --verbose --site test_site install-app erpnextswiss
