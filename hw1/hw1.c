
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

int globalSize = 128;
// Function to convert a given word into it's hash equivalent
int hash_function(char* word, int size) {
	
	int sum = 0;
	int i = 0;
	int length = strlen(word);
	while (i < length){
		sum += (int) * (word + i);
		i = i + 1;
	}
	return sum % size;
}


void printAndFreeCache(char** cache, int size) {
    int i;
    for (i = 0; i < size; i++) {
        if (*(cache + i) == NULL) {
            continue;
        }

        printf("Cache index %d ==> \"%s\"\n", i, *(cache + i));
        free(*(cache + i));
    }
}

char* reallocFuncTest(const char* offset) {
    char* new_entry = calloc(strlen(offset) + 1, sizeof(char));
    strcpy(new_entry, offset);
    return new_entry;
}

void reallocFunc(char** cache, int curr_hash, const char* offset) {
    printf("Word \"%s\" ==> %d (realloc)\n", offset, curr_hash);
    *(cache + curr_hash) = (char*)realloc(*(cache + curr_hash), strlen(offset) + 1);
    strcpy(*(cache + curr_hash), offset);
}

void callocFunc(char** cache, int curr_hash, const char* offset) {
    printf("Word \"%s\" ==> %d (calloc)\n", offset, curr_hash);
    char* new_entry = calloc(strlen(offset) + 1, sizeof(char));
    strcpy(new_entry, offset);
    *(cache + curr_hash) = new_entry;
}

int main(int argc, char** argv) {

	// In the case that there are not enough arguments 
	if (argc < 3){
		fprintf(stderr, "STDERR: Not enough args\n");
		return EXIT_FAILURE; 
	}
	//take input string of cache size and make it an integer
	int size = atoi(*(argv + 1));
	if (size == 0 && *(argv+1) != 0){
		fprintf(stderr, "STDERR: unvalid cache size argument\n");
		return EXIT_FAILURE;
	}

	FILE *fp; 
	fp = fopen(*(argv + 2), "r");

	if (fp == NULL){
		fprintf(stderr, "STDERR: invalid text file\n");
		return EXIT_FAILURE;
	}else{
		char** story = calloc(size, sizeof(char*));
		char* offset = calloc(globalSize, sizeof(char));
		int ptr = 0;
		while (fp){
			if (feof(fp)) {
				break;
			}
			char temp = fgetc(fp);
			if (!isalnum(temp)){
				*(offset+ptr) = '\0';
				if (strlen(offset) > 2){
					int curr_hash = hash_function(offset, size);

					if (*(story + curr_hash) != 0){
						reallocFunc(story,curr_hash, offset);
					}
					else {
						callocFunc(story,curr_hash,offset);
					}
				}

				memset(offset, 0, globalSize);
				ptr = 0;
			}
			else {
				*(offset+ptr) = temp;
				ptr += 1;
			}
		}
		free(offset);
		printAndFreeCache(story,size);
		free(story);
		fclose(fp);
		return EXIT_SUCCESS;
	}
}