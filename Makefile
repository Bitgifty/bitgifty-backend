build:
	git pull
	sudo docker build . -t giftcarded:v1
	sudo docker stop $(shell docker ps -a -q)
	sudo docker run -d -p 80:8000 giftcarded:v1

