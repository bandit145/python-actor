#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <limits.h>
#include <assert.h>
#include <stdlib.h>

// 32 bit FNV values
#define FNV_PRIME 16777619
#define FNV_OFFSET_BASIS 2166136261

typedef struct HashMap {
	char values[1000];
	long size;
} HashMap;


long hash_fnv(char data[]){
	long hash = FNV_OFFSET_BASIS;
	for ( int i = 0;  data[i] != '\0'; ++i){
		hash += hash * FNV_PRIME;
		hash += hash ^ data[i];
	};
	return hash;

};

// void insert_key(char key[], char value[], HashMap *map){
// 	long hash = hash_fnv(key);

// };

int main(void){
	struct HashMap map;
	map.size = 1000;
	char thing[] = "data";
	long hash = hash_fnv(thing);
	printf("Hash: %ld", hash);
	printf("Location: %ld", hash % map.size);
	// insert_key("Hello", "Hi?");
	// insert_key("Begone", "ok!");
};

