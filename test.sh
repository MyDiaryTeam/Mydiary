set -eo pipefail

COLOR_GREEN=$(tput setaf 2)
COLOR_NC=$(tput sgr0) # No Color

echo "Starting black"
uv run black .
echo "성~~~공~~띠~~~"

echo "Starting isort"
uv run isort .
echo "앙 ~ 성공띠 ~"

echo "starting ruff"
uv run ruff check --fix
echo "성공띠 ~"

echo "starting Mypy"
uv run mypy .
echo "성공띠 ~"


echo "${COLOR_GREEN}ALL tests passed successfully!${COLOR_NC}"

