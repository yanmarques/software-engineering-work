# discover pip path, try pip3 fallback to just pip
pip_path=$(which pip3 || which pip)

# install requirements
exec $pip_path install requests scrapy scrapy_cookies > /dev/null
