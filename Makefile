build:
	git pull
	sudo docker build . -t giftcarded:v1
	sudo docker stop $(docker ps -a -q)
	sudo docker run giftcarded:v1 -d -p 8000:8000

