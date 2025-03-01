//March 21, 2024
//Devanshu Haldar
//OpSys Homework 3
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>

// Global Variables
int max_squares;
int*** boards;
int board_length; 
int board_count;
int x; 
pthread_t mainThread;

int global_value = 8;


pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
#define FREE_BOARD(b, len) do { \
    for (int k = 0; k < (len); k++) { \
        free((b)[k]); \
    } \
    free(b); \
} while (0)

//FOUND ABOVE ONLINE TO SUPPORT THE CODE BELOW IN ADD BOARD

void addBoard(int rows, int cols, int** board, int seen){
    if (seen >= x) {
        pthread_mutex_lock(&mutex);
        if (board_count + 1 >= board_length) {
            board_length += 10;
            boards = realloc(boards, board_length * sizeof(int***));
        }
        boards[board_count++] = board;

        pthread_mutex_unlock(&mutex);
    } else {
        FREE_BOARD(board,rows);
    }//cols not need used

    return;
}

void freeBoards(int rows){
	int i = 0;
    int j;
	while (i < board_count){
        j = 0;
		while (j < rows){
			free(boards[i][j]);
            j+=1;
		}
		free(boards[i]);
        i+=1;
	}
	free(boards);
	return;
}

 
void print_board(int rows, int cols){
	printf("THREAD %ld: Dead end boards:\n", pthread_self());
	int i, j, k;

    i = 0;
	while (i < board_count){

		printf("THREAD %ld: > ", pthread_self());
        j = 0;
		while ( j < rows ){
			if (j == 0) 
            {// printf("Thread failure");
            } else { printf("THREAD %ld:   ", pthread_self());	}
            k = 0;
			while ( k < cols){
				if (boards[i][j][k] != 0){
                    printf("S");
				}
				else {
					printf(".");
				}
                k+=1;
			}
		    printf("\n");
            j+=1;
		}
        i+=1;
	}
	return;
}

void searchPotentialMoves(int** board, int* currPos, int rows, int cols, int* t_count, int** next) {
    int moves[8][2] = {
        {-1, -2}, {-2, -1}, {-2, 1}, {-1, 2},
        {1, 2}, {2, 1}, {2, -1}, {1, -2}
    };

    *t_count = 0; 

    for (int i = 0; i < global_value; i++) {
        int newRow = currPos[0] + moves[i][0];
        int newCol = currPos[1] + moves[i][1];

        if (newRow >= 0 && newRow < rows && newCol >= 0 && newCol < cols && board[newRow][newCol] == 0) {
            next[*t_count][0] = newRow;
            next[*t_count][1] = newCol;
            (*t_count)++;
        } else {
            next[i][0] = 0;
            next[i][1] = 0;
        }
    }
}

struct process_obj {
	int** board;
	int rows;
	int cols;
	int curr;
	int currPos[2];
	int seen;
};

void* next_calculation(void* args);

void handleSingleMoveScenario(int** board, int** next, int rows, int cols, int curr, int seen) {
  
    int nextPos[2] = {-1, -1}; 
    int i = 0;
    while( i < global_value) {
        if (next[i][0] != 0 || next[i][1] != 0) {
            nextPos[0] = next[i][0];
            nextPos[1] = next[i][1];
            break;
        }
        i+=1;
    }

    if (nextPos[0] != -1 && nextPos[1] != -1) { 
        board[nextPos[0]][nextPos[1]] = curr + 1;
        struct process_obj* nextArgs = malloc(sizeof(struct process_obj));
        if (nextArgs != NULL) { 
            nextArgs->board = board;
            nextArgs->rows = rows;
            nextArgs->cols = cols;
            nextArgs->curr = curr + 1;
            nextArgs->currPos[0] = nextPos[0];
            nextArgs->currPos[1] = nextPos[1];
            nextArgs->seen = seen + 1;
            next_calculation(nextArgs);
        }
    }

    // Clean up next
    i = 0;
    while( i < global_value) {
        free(next[i]);
        i+=1;
    }
    free(next);
}

void createAndRunThreadForMove(int** originalBoard, int rows, int cols, int moveIndex, int curr, int* currPos, int seen, pthread_t* threat_t_id) {
    int** newBoard = calloc(rows, sizeof(int*));
    for (int j = 0; j < rows; j++) {
        newBoard[j] = calloc(cols, sizeof(int));
        for (int k = 0; k < cols; k++) {
            newBoard[j][k] = originalBoard[j][k];
        }
    }

    newBoard[currPos[0]][currPos[1]] = curr + 1;

    struct process_obj* args = malloc(sizeof(struct process_obj));
    if (args) { 
        args->board = newBoard;
        args->rows = rows;
        args->cols = cols;
        args->curr = curr + 1;
        args->currPos[0] = currPos[0];
        args->currPos[1] = currPos[1];
        args->seen = seen + 1;


        pthread_create(&threat_t_id[moveIndex], NULL, next_calculation, args);
    } else {
        // Handle malloc failure (e.g., log error, clean up resources)
    }
}
void freeBoard(int** board, int rows) {
    for (int i = 0; i < rows; i++) {
        free(board[i]);
    }
    free(board);
}

void freeMoves(int** next, int count) {
    for (int i = 0; i < count; i++) {
        free(next[i]);
    }
    free(next);
}

void handleKnightTour(int** board, int rows) {
    printf("THREAD %ld: Sonny found a full knight's tour!\n", pthread_self());
    freeBoard(board, rows);
}

void handleDeadEnd(int** board, int rows, int cols, int curr, int seen) {
    printf("THREAD %ld: Dead end after move #%d\n", pthread_self(), curr);
    addBoard(rows, cols, board, seen); // Assuming implementation elsewhere
}

void handleNoMoreMoves(struct process_obj* args, int** next, int* returnSize) {
    // Helper function calls to free dynamic memory and handle specific scenarios
    if (args->seen == args->rows * args->cols) {
        handleKnightTour(args->board, args->rows);
    } else {
        handleDeadEnd(args->board, args->rows, args->cols, args->curr, args->seen);
    }

    // Update max_squares if seen is greater, assuming max_squares is accessible here
    if (args->curr > max_squares) {
        max_squares = args->curr;
    }

    // Clean up and exit the thread
    freeMoves(next, global_value);
    free(args);
    *returnSize = args->curr;
    pthread_exit(returnSize);
}

void* next_calculation(void* args){

	struct process_obj* next_args = args;

	int** board;
	int rows, cols; 
	int curr; 
	int currPos[2];
	int seen;
	int highest;

	board = next_args->board;
	rows = next_args->rows;
	cols = next_args->cols;
	curr = next_args->curr;
	currPos[0] = next_args->currPos[0];
	currPos[1] = next_args->currPos[1];
	seen = next_args->seen;	

	highest = curr;

	int* returnSize = malloc(1*sizeof(int));
	*returnSize = 0;

	if (curr == 1){
		printf("THREAD %ld: Solving Sonny's knight's tour problem for a %dx%d board\n", pthread_self(), rows, cols);
	}

	int t_count = 0; 

	int** next = calloc(global_value, sizeof(int*));

	int i = 0;
    while (i < global_value){
		next[i] = calloc(2, sizeof(int));
        i+=1;
	}

	searchPotentialMoves(board, currPos, rows, cols, &t_count, next); 

	if (t_count == 1){
        handleSingleMoveScenario(board, next, rows, cols, curr, seen);
	}

	// In the case that there are more than one possible move
	else if (t_count > 1){

		free(next_args);
		printf("THREAD %ld: %d moves possible after move #%d; creating threads...\n", pthread_self(), t_count, curr);

		pthread_t threat_t_id[global_value];

		
		for (int i = 0; i < global_value; i++){
			if (!(next[i][0] == 0 && next[i][1] == 0)){

				// Create a new board for this specific move 
				int** newBoard = calloc(rows, sizeof(int*));
				int j,k;
				for (j = 0; j < rows; j++){
					newBoard[j] = calloc(cols, sizeof(int));
					for (k = 0; k < cols; k++){
						newBoard[j][k] = board[j][k];
					}
				}

				newBoard[next[i][0]][next[i][1]] = curr + 1;

				int currPos[2];
				currPos[0] = next[i][0];
				currPos[1] = next[i][1];

				struct process_obj* args = malloc(sizeof(struct process_obj));
				args->board = newBoard;
				args->rows = rows;
				args->cols = cols;
				args->curr = curr + 1;
				args->currPos[0] = currPos[0];
				args->currPos[1] = currPos[1];
				args->seen = seen + 1;

				pthread_create(&threat_t_id[i], NULL, &next_calculation, args);

				#ifdef NO_PARALLEL 
				void* returnValue = malloc(0);
				free(returnValue);

				pthread_join(threat_t_id[i], (void**) &returnValue);

				if (*(int*) returnValue > highest){
					highest = *(int*) returnValue;
				}	

				printf("THREAD %ld: Thread [%ld] joined (returned %d)\n", pthread_self(), threat_t_id[i], *(int*) returnValue);
				free(returnValue);
				#endif

			}
		}

		#ifndef NO_PARALLEL
			
			for (i = 0; i < global_value; i++){
				if (next[i][0] != 0 && next[i][1] != 0){
					
					void* returnValue = malloc(0); 
					free(returnValue);

					pthread_join(threat_t_id[i], (void**) &returnValue);		
					
					if (*(int*) returnValue > highest){
						highest = *(int*) returnValue;
					}			

					printf("THREAD %ld: Thread [%ld] joined (returned %d)\n", pthread_self(), threat_t_id[i], highest);
					free(returnValue);
				}
			}
	
		#endif

		for (i = 0; i < global_value; i++){
			free(next[i]);
		}
		free(next);
	}

    else if (t_count == 0){
        int* returnSize = malloc(sizeof(int)); // Ensure this allocation is done before calling the function
        handleNoMoreMoves(next_args, next, returnSize);
    }

	if (pthread_self() != mainThread){

		*returnSize = curr;
		if (highest > *returnSize){
			*returnSize = highest;
		}

		for (i = 0; i < rows; i++){
			free(board[i]);
		}
		free(board);

		pthread_exit(returnSize);
	}

	free(returnSize);
	return returnSize;
}




int main(int argc, char** argv){
	if (argc < 3){
		fprintf(stderr, "ERROR: Invalid argument(s)\n");
		fprintf(stderr, "USAGE: a.out <m> <n> [<x>]\n");
		return EXIT_FAILURE;	
	}
    
	setvbuf( stdout, NULL, _IONBF, 0 );

	int rows = atoi(argv[1]);
	int cols = atoi(argv[2]);
    
    if (argc != 4){
        x = 0;
	}
	else {
		x = atoi(argv[3]);
	}

    if (!(rows > 2 && cols > 2)){
		fprintf(stderr, "ERROR: Invalid argument(s)\n");
		fprintf(stderr, "USAGE: a.out <m> <n> [<x>]\n");
		return EXIT_FAILURE;	
	}

    if (argc == 4) {
		int sum = rows * cols;
		if (x > sum){
			fprintf(stderr, "ERROR: Invalid argument(s)\n");
			fprintf(stderr, "USAGE: a.out <m> <n> [<x>]\n");
			return EXIT_FAILURE;	
		}
	}
    

	

	
	max_squares = 0;
	boards = calloc(10, sizeof(int**));
	board_length = 10; 
	board_count = 0;

	
	int** board = calloc(rows, sizeof(int*));
	int i = 0;
    while ( i < rows ){
		board[i] = calloc(cols, sizeof(int));
		for (int j = 0; j < cols; j++){
			board[i][j] = 0;
		}
        i+=1;
	}

	board[0][0] = 1; 
	int currPos[2]; 
    for (int i = 0; i < 2; i++){
        currPos[i] = 0;
    }
	

	struct process_obj* args = malloc(sizeof(struct process_obj));

	args->board = board;
	args->rows = rows;
	args->cols = cols;
	args->curr = 1;
	args->currPos[0] = currPos[0];
	args->currPos[1] = currPos[1];
	args->seen = 1;

	mainThread = pthread_self();
	next_calculation(args);

	printf("THREAD %ld: Best solution(s) found visit %d squares (out of %d)\n", pthread_self(), max_squares, rows * cols);

	print_board(rows, cols);
	freeBoards(rows); 

	pthread_mutex_destroy(&mutex);

    while (i < rows){
        free(board[i]);
        i+=1;
    }
    free(board);


	return EXIT_SUCCESS;
}