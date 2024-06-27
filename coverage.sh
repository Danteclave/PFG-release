coverage run -m unittest discover -s . -p "test_*.py"

coverage html

firefox htmlcov/index.html
