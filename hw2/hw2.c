
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

void checkChildren(int* childProcessCount){
	
        int i = 0;
		while (i < *childProcessCount){
            int status;

			int curr_pid = waitpid(-1, &status, WNOHANG);

			if (curr_pid == 0){
				continue;
			}

			if (!WIFSIGNALED(status)) {
				printf("[process %d terminated with exit status %d]\n", curr_pid, WEXITSTATUS(status));
				*childProcessCount -= 1;
            }
			else {
                printf("[process %d terminated abnormally]\n", curr_pid);
				*childProcessCount -= 1;
			}
            i++;
        }
}

void tokenizeInput(char* userInput, char** token_array, int* count_token) {
    *count_token = 0;
    char* token = strtok(userInput, " ");

    while (token != NULL) {
        char* currToken = calloc(65, sizeof(char));
        strcpy(currToken, token);
        token_array[*count_token] = currToken;
        (*count_token) += 1;
        token = strtok(NULL, " ");
    }
}

int checkForPipe(char** token_array, int count_token, int* pipeIndex) {
    int containsPipe = 0;

    for (int i = 0; i < count_token; i++) {
        if (!strcmp(token_array[i], "|")) {
            containsPipe = 1;
            *pipeIndex = i;
            break;
        }
    }

    return containsPipe;
}

int directory_change_test(){
    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        printf("Current working directory: %s\n", cwd);
    } else {
        perror("getcwd");
        return 1;
    }

    // Change directory to a specified path
    const char* newDir = "/path/to/your/directory";
    if (chdir(newDir) != 0) {
        perror("chdir");
        return 1;
    }

    // Get and print the updated current working directory
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        printf("Changed working directory: %s\n", cwd);
    } else {
        perror("getcwd");
        return 1;
    }

    return 0;
}

void handleCdCommand(char** token_array, int count_token, char** current_path) {
    int success;

    if (!strcmp(token_array[0], "cd")) {
 
        if (count_token == 1) {
            success = chdir(getenv("HOME"));

            if (success == 0) {
                free(*current_path);
                *current_path = calloc(strlen(getenv("HOME")) + 1, sizeof(char));
                strcpy(*current_path, getenv("HOME"));
            }
        }
     
        else if (!strcmp(token_array[1], "/")) {
            success = chdir("/");

            if (success == 0) {
                free(*current_path);
                *current_path = calloc(pathconf(".", _PC_PATH_MAX) + 1, sizeof(char));
                getcwd(*current_path, pathconf(".", _PC_PATH_MAX));
            }
        }
     
        else {
        }

        for (int i = 0; i < count_token; i++) {
            if (token_array[i] != NULL) {
                free(token_array[i]);
            }
        }
    }
}

int test_process(){
    pid_t child_pid;

    // Create a new process
    child_pid = fork();

    if (child_pid == -1) {
        // Error handling for fork failure
        perror("fork");
        return 1;
    }

    if (child_pid == 0) {
        // Child process
        printf("Child process executing...\n");

        // Example: execute the "ls" command using execl
        execl("/bin/ls", "ls", "-l", (char *)NULL);

        // execl only returns if there is an error
        perror("execl");
        return 1;
    } else {
        // Parent process
        printf("Parent process waiting for the child...\n");

        // Wait for the child process to complete
        wait(NULL);

        printf("Parent process exiting.\n");
    }

    return 0;
}

void changeDirectory(char** current_path, int count_token, char** token_array){
    int success;
    if (count_token == 1){
        success = chdir(getenv("HOME"));

        if (success == 0){
            free(current_path);
            *current_path = calloc(strlen(getenv("HOME") + 1), sizeof(char));
            strcpy(*current_path, getenv("HOME"));
        }
    }

    else if (!strcmp(token_array[1], "/")){
        success = chdir("/");

        if (success == 0){
            free(*current_path);
            *current_path = calloc(pathconf(".", _PC_PATH_MAX) + 1, sizeof(char));
            getcwd(*current_path, pathconf(".", _PC_PATH_MAX));
        }
    }

    else {
        free(*current_path);
        *current_path = calloc(pathconf(".", _PC_PATH_MAX) + 1, sizeof(char));	
        getcwd(*current_path, pathconf(".", _PC_PATH_MAX));

        char* temp = calloc(900, sizeof(char));
        strcpy(temp, *current_path);

        temp[strlen(temp)] = '/';
        
        int i;
        for (i = 0; i < strlen(token_array[1]); i++) {
            temp[strlen(temp)] = token_array[1][i];
        }

        temp[strlen(temp)] = '\0';

        success = chdir(token_array[1]);

        if (success == 0){
            free(*current_path);
            *current_path = calloc(pathconf(".", _PC_PATH_MAX) + 1, sizeof(char));	
            getcwd(*current_path, pathconf(".", _PC_PATH_MAX));
        }
        else{
            fprintf(stderr, "chdir() failed: Not a directory\n");
        }
        free(temp);
    }
}

int main(int argc, char** argv) {

	setvbuf( stdout, NULL, _IONBF, 0 );

	long size = pathconf(".", _PC_PATH_MAX);
    int sizeofchar = sizeof(char);
	char* current_path = calloc(size, sizeofchar);	
	current_path = getcwd(current_path, (size_t) size);
	char** pathContainer = calloc(50, sizeof(char*)); 

	char* MYPATH = calloc(900, sizeofchar);
	if (getenv("MYPATH") != NULL){
        strcpy(MYPATH, getenv("MYPATH"));
	} else {
		strcpy(MYPATH, "/bin:.");
	}

	char* path = strtok(MYPATH, ":");
	int pathCount = 0;

	while (path != NULL){
		pathContainer[pathCount] = calloc(100, sizeofchar); 
		strcpy(pathContainer[pathCount], path);
		pathContainer[pathCount][strlen(pathContainer[pathCount])] = '\0';
		pathCount += 1;
		path = strtok(NULL, ":");
	}

	int childProcessCount = 0; 
	for(;;){	
		char* userInput = calloc(1024, sizeof(char));
		char** token_array = calloc(16, sizeof(char*));
		checkChildren(&childProcessCount);
		printf("%s$ ", current_path);
		fgets(userInput, 1024, stdin);
		userInput[strlen(userInput) - 1] = '\0';
		if (!strcmp(userInput, "exit")) {
			
			for ( int i = 0; i < 16; i++){
				if (token_array[i] != NULL){
					free(token_array[i]);
				}
			}
			free(token_array);
		    free(userInput);
			break;
		}

        int count_token = 0;
        tokenizeInput(userInput, token_array, &count_token);

	    int pipeIndex = 0;

        int containsPipe = checkForPipe(token_array, count_token, &pipeIndex);


        // handleCdCommand(token_array, count_token, &current_path);
		if (!strcmp(token_array[0], "cd")){

            changeDirectory(&current_path, count_token,token_array);
			int i;
			for (i = 0; i < count_token; i++){
				if (token_array[i] != NULL){
					free(token_array[i]);
				}
			}
			free(token_array);
		    free(userInput);
			continue; 
		}

		int execution_found = 0;
		int execution_one_found = 0;
		int execution_two_found = 0;
		int pathIndex[2];

		if (containsPipe) {
			int j;
			for (j = 0; j < 2; j++){
				int i;
				int commandIndex = 0;

				if (j == 1){
					commandIndex = pipeIndex + 1;
				}

				for (i = 0; i < pathCount; i++){
					if (pathContainer[i] == NULL){
						break;
					}
					pathIndex[j] = i;

					char* tempPath = calloc(200, sizeof(char));
					strcpy(tempPath, pathContainer[i]);

					tempPath[strlen(tempPath)] = '/';

					int k;
					for (k = 0; k < strlen(token_array[commandIndex]); k++){
						tempPath[strlen(tempPath)] = token_array[commandIndex][k];
					}

					struct stat buf;
					int rc= lstat(tempPath, &buf);
					free(tempPath);

					if (rc == 0){
						if (buf.st_mode & S_IXUSR){
							if (j == 0){
								execution_one_found = 1;
							}
							if (j == 1){
								execution_two_found = 1;
							}
						}
						break;
					}
				}
			}
		}

		else {

			int i;
			for (i = 0; i < pathCount; i++){	
				if (pathContainer[i] == NULL){
					break;
				}

				pathIndex[0] = i;

				char* tempPath = calloc(200, sizeof(char));
				strcpy(tempPath, pathContainer[i]);

				tempPath[strlen(tempPath)] =  '/';
				int j; 
				for (j = 0; j < strlen(token_array[0]); j++){
					tempPath[strlen(tempPath)] = token_array[0][j];
				}

				struct stat buf;
				int rc = lstat(tempPath, &buf);

				free(tempPath);

				if (rc == 0){

					if (buf.st_mode & S_IXUSR){
						execution_found = 1;
					} 
					break;
				}
			}
		}

		if (containsPipe && (execution_one_found == 0 || execution_two_found == 0)){
			fprintf(stderr, "ERROR: one or both of the commands not found");
		}

		else if (!containsPipe && execution_found == 0){
			fprintf(stderr, "ERROR: command \"%s\" not found\n", token_array[0]);
		}

		else if (execution_found != 0 && !containsPipe) {
			char* exec = calloc(strlen(token_array[0]) + strlen(pathContainer[pathIndex[0]]) + 2, sizeof(char));
			strcpy(exec, pathContainer[pathIndex[0]]);
			exec[strlen(exec)] = '/';

			int i;
			for (i = 0; i < strlen(token_array[0]); i++){
				exec[strlen(exec)] = token_array[0][i];
			}


			exec[strlen(exec)] = '\0';

			int isBackground = 0; 
		
			if (strcmp(token_array[count_token-1], "&") == 0){
				isBackground = 1;
				free(token_array[count_token - 1]);
				token_array[count_token - 1] = '\0';
			}		 

			pid_t pid;
			pid = fork();

			if (pid == -1){
				perror("Failed to fork...");
				return EXIT_FAILURE;
			}

			if (pid == 0){
				execv(exec, token_array);
				perror("EXEC FAILED\n");
				return EXIT_FAILURE;
			}

			else if (pid > 0){
				if (isBackground == 0){

					waitpid(pid, NULL, 0);
				}
				else{
					printf("[running background process \"%s\"]\n", token_array[0]);
					childProcessCount += 1;
					int child_pid = waitpid(-1, NULL, WNOHANG);
					
					if (child_pid == -1){
						perror("waitpid() error\n" );
						return EXIT_FAILURE;
					}
				}
 			}
			free(exec);
		}

		else if (execution_one_found != 0 && execution_two_found != 0 && containsPipe){
			
			int isBackground = 0; 
		
			if (strcmp(token_array[count_token-1], "&") == 0){
				isBackground = 1;
				free(token_array[count_token - 1]);
				token_array[count_token - 1] = '\0';
				count_token -= 1;
			}		 

			int i;

			char* execution_one = calloc(strlen(token_array[0]) + strlen(pathContainer[pathIndex[0]]) + 2, sizeof(char));
			strcpy(execution_one, pathContainer[pathIndex[0]]);
			execution_one[strlen(execution_one)] = '/';

			for (i = 0; i < strlen(token_array[0]); i++){
				execution_one[strlen(execution_one)] = token_array[0][i];
			}
			execution_one[strlen(execution_one)] = '\0';

			
			char** argsOne = calloc(pipeIndex + 1, sizeof(char*));
			int argsCountOne = 0;

			for (i = 0; i < pipeIndex; i++){
				argsOne[i] = calloc(strlen(token_array[i]) + 1, sizeof(char));
				strcpy(argsOne[i], token_array[i]);
				argsCountOne += 1;
			}

			
			char* execution_two = calloc(strlen(token_array[pipeIndex + 1]) + strlen(pathContainer[pathIndex[1]]) + 2, sizeof(char));
			strcpy(execution_two, pathContainer[pathIndex[1]]);
			execution_two[strlen(execution_two)] = '/';

			for (i = 0; i < strlen(token_array[pipeIndex + 1]); i++){
				execution_two[strlen(execution_two)] = token_array[pipeIndex + 1][i];
			}
			execution_two[strlen(execution_two)] = '\0';

			
			char** argsTwo = calloc(count_token - pipeIndex, sizeof(char*));
			int argsCountTwo = 0;

			for (i = pipeIndex + 1; i < count_token; i++){
				argsTwo[argsCountTwo] = calloc(strlen(token_array[i]) + 1, sizeof(char));
				strcpy(argsTwo[argsCountTwo], token_array[i]);
				argsCountTwo += 1;
			}


			
			int pipefd[2]; 
			int rc = pipe(pipefd);
			if (rc == -1){
				perror("Pipe creation failed\n");
				return EXIT_FAILURE;
			}

			
			pid_t pid1;
			pid1 = fork();
			if (pid1 == -1){
				perror("Failed to fork...\n");
				return EXIT_FAILURE;
			}

			
			if (pid1 == 0){
				
				close(pipefd[0]);
				close(1);
				dup2(pipefd[1], 1);
				close(pipefd[1]);
				execv(execution_one, argsOne);
				perror("EXEC ONE FAILED\n");
				return EXIT_FAILURE;
			}

			pid_t pid2;
			pid2 = fork();
			if (pid2 == -1){
				perror("Failed to fork...\n");
				return EXIT_FAILURE;
			}
			
			if (pid2 == 0 && pid1 > 0){
				
				close(pipefd[1]);
				close(0);
				dup2(pipefd[0], 0);	
				close(pipefd[0]);
				execv(execution_two, argsTwo);
				perror("EXEC TWO FAILED\n");
				return EXIT_FAILURE;
			}

			if (pid2 > 0 && pid1 > 0){
				
				close(pipefd[0]);
				close(pipefd[1]);

				if (!isBackground) {
					waitpid(pid2, NULL, WUNTRACED | WCONTINUED);
					waitpid(pid1, NULL, WUNTRACED | WCONTINUED);
				}

				else {
					printf("[running background process \"%s\"]\n", token_array[0]);
					printf("[running background process \"%s\"]\n", token_array[count_token - pipeIndex]);
					
					childProcessCount += 2;
					int child_1 = waitpid(-1, NULL, WNOHANG);
					int child_2 = waitpid(-1, NULL, WNOHANG);

					if (child_1 == -1){
						perror("waitpid() error\n");
						return EXIT_FAILURE;
					}

					if (child_2 == -1){
						perror("waitpid() error\n");
						return EXIT_FAILURE;
					}
				}

				
				for (i = 0; i < argsCountOne + 1; i++){
					free(argsOne[i]);
				}
				free(argsOne);
				for (i = 0; i < argsCountTwo + 1; i++){
					free(argsTwo[i]);
				}
				free(execution_one);
				free(execution_two);
				free(argsTwo);

			}
			
			if (!(pid1 > 0 && pid2 > 0)){
				exit(1);
			}
		}

		
		int i;
		for (i = 0; i < 16; i++){
			if (token_array[i] != NULL){
				free(token_array[i]);
			}
		}
		free(token_array);
	    free(userInput);
	}

	printf("bye\n");

	int i;
	for (i = 0; i < 50; i++){
		if (pathContainer[i] != NULL){
			free(pathContainer[i]);
		}
	}

	free(pathContainer);
	free(current_path);
	free(MYPATH);

	return EXIT_SUCCESS;
}