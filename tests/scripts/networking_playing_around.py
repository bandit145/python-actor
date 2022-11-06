#!/usr/bin/env python3

from actor.system.networking import NetworkMessageServer


def main():
	server = NetworkMessageServer()
	server.start()
	while True:
		pass

if __name__ == '__main__':
	main()