#! /bin/sh

if [ "$1" = "clean" ]; then
	rm -f ./*.pyc
else
	echo 'Usage: ./make.sh clean'
fi
