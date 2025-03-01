/* hw4-client.c */
//Devanshu Haldar
//Operating Systems Homework 4
//4/23/2024




// #include <stdio.h>
// #include <stdlib.h>
// #include <string.h>
// #include <unistd.h>
// #include <sys/types.h>
// #include <sys/socket.h>
// #include <netinet/in.h>
// #include <pthread.h>

// #define PORT 5757 

// void *client_handler(void *socket_desc);

// int main()
// {
//     int server_fd, new_socket;
//     struct sockaddr_in address;
//     int opt = 1;
//     int addrlen = sizeof(address);
//     pthread_t thread_id;

//     // Create a socket file descriptor
//     if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
//     {
//         perror("socket failed");
//         exit(EXIT_FAILURE);
//     }

//     // Set socket options
//     if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)))
//     {
//         perror("setsockopt");
//         exit(EXIT_FAILURE);
//     }

//     // Assign IP and port
//     address.sin_family = AF_INET;
//     address.sin_addr.s_addr = INADDR_ANY;
//     address.sin_port = htons(PORT);

//     // Bind the socket to the address and port
//     if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
//     {
//         perror("bind failed");
//         exit(EXIT_FAILURE);
//     }

//     // Listen for incoming connections
//     if (listen(server_fd, 3) < 0)
//     {
//         perror("listen");
//         exit(EXIT_FAILURE);
//     }

//     printf("Server listening on port %d\n", PORT);

//     while (1)
//     {
//         // Accept incoming connections
//         if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen)) < 0)
//         {
//             perror("accept");
//             exit(EXIT_FAILURE);
//         }

//         // Create a new thread for each client
//         if (pthread_create(&thread_id, NULL, client_handler, (void *)&new_socket) < 0)
//         {
//             perror("could not create thread");
//             exit(EXIT_FAILURE);
//         }

//         // Detach the thread to avoid memory leaks
//         pthread_detach(thread_id);
//     }

//     return 0;
// }

// void *client_handler(void *socket_desc)
// {
//     int sock = *(int *)socket_desc;
//     int read_size;
//     char client_message[2000];

//     while ((read_size = recv(sock, client_message, 2000, 0)) > 0)
//     {
//         // Handle the client message here
//         printf("Received message: %s\n", client_message);

//         // Send a response back to the client
//         send(sock, client_message, strlen(client_message), 0);
//     }

//     if (read_size == 0)
//     {
//         printf("Client disconnected\n");
//         fflush(stdout);
//     }
//     else if (read_size == -1)
//     {
//         perror("recv failed");
//     }

//     close(sock);
//     pthread_exit(NULL);
// }
#include <sys/types.h>
#include <pthread.h>
#include <signal.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <strings.h>
#include <unistd.h>
#include <ctype.h>


extern int total_guesses;
extern int total_wins;
extern int total_losses;
extern char ** words;
int total_words;

pthread_t* tids = NULL;
long num_tids = 0;
int* server_fds = NULL;
long servers = 0;
void ** dynamically_allocated_memory = NULL;
int dynamic_blocks = 0;
int sent_kill_signals = 0;
long unsigned int parent_thread;

char** words_played = NULL;
int num_words_played = 0;

int received;


#define MAXBUFFER 5
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

//helper funcs for understanding
void check_pthread_error(int return_code, const char *message) {
    if (return_code != 0) {
        fprintf(stderr, "pthread error: %s\n", message);
        exit(EXIT_FAILURE);
    }
}

void *thread_function(void *args) {
    printf("Hello from thread %ld!\n", pthread_self());
    return NULL; 
}

void start_thread() {
    pthread_t thread;
    int rc = pthread_create(&thread, NULL, thread_function, NULL);
    check_pthread_error(rc, "Creating thread failed");

    rc = pthread_join(thread, NULL);
    check_pthread_error(rc, "Joining thread failed");
}

void* allocation(int n, int size) {
    dynamically_allocated_memory = realloc(dynamically_allocated_memory, (dynamic_blocks + 1) * sizeof(void**)); 
    void* ptr = calloc(n, size);
    *((void**)dynamically_allocated_memory + dynamic_blocks) = ptr;  
    dynamic_blocks = dynamic_blocks + 1;
    return ptr;
}

int pthread_allocation(pthread_attr_t* attr, void*(*start_routine) (void*), void* arg) {
    pthread_t* tid = calloc(1, sizeof(pthread_t));
    int rc = pthread_create(tid, attr, start_routine, arg);
    tids = realloc(tids, (num_tids + 1) * sizeof(pthread_t));
    *((pthread_t*)tids + num_tids) = *tid; 
    free(tid);
    num_tids = num_tids + 1;
    return rc;
}

int accept_and_save(int sockfd, struct sockaddr *restrict addr, socklen_t *restrict addrlen) {
    int newsd = accept(sockfd, addr, addrlen);
    long temp = servers + 1;
    server_fds = realloc(server_fds, temp * sizeof(int));
    *((int*)server_fds + servers) = newsd;  
    servers = servers + 1;
    return newsd;
}


int initialize_tcp_server(int port) {
    
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (server_fd == -1) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 5) == -1) {
        perror("listen failed");
        exit(EXIT_FAILURE);
    }

    return server_fd;
}
void pthread_detach_and_save(pthread_t tid){
    int i = 0; 
    while (i < num_tids){
        if(*(tids+i) == tid){
            for(int j = i+1;j<num_tids;j++){
                *(tids+j-1) = *(tids+j);
            }
            num_tids--;
            break;
        }
        i++;
    }
    pthread_detach(tid);
    tids = realloc(tids, sizeof(pthread_t)*num_tids);
}


char* upper(char* s){
    char* ret = allocation(strlen(s)+1, 1);
    int i = 0;
    int length = strlen(s);
    while (i < length){
        *(ret+i) = toupper(*(s+i));
        i++;
    }
    return ret;
}

void signal_handler( int sig ){
  if ( sig != SIGUSR1 ){
      while(!sent_kill_signals){
              sleep(0.25);
          }
          pthread_mutex_lock(&mutex);
              pthread_detach_and_save(pthread_self());
          pthread_mutex_unlock(&mutex);
      }
      else{
        if(parent_thread == pthread_self()){
          printf("MAIN: SIGUSR1 rcvd; Wordle server shutting down...\n");
        
          int i = 0;
          while ( i < servers ){
              close(*(server_fds+i));
              i++;
          }
          servers = 0;
          pthread_t* current_tid = tids;
          while (current_tid < tids + num_tids) {
            pthread_kill(*current_tid, SIGUSR1);
            current_tid++;
          }
          sent_kill_signals = 1;
  
          while (num_tids > 0){
              sleep(0.1);
          }

          close(received);
          printf("MAIN: Wordle server shutting down...\n");
          printf("\nMAIN: guesses: %d\nMAIN: wins: %d\nMAIN: losses: %d\n\nMAIN: word(s) played:", total_guesses, total_wins, total_losses);
          for(int i = 0;i<num_words_played;i++){
              printf(" %s", upper(*(words_played+i)));
          }
          printf("\n");
        
          i = 0; 
          while (i < dynamic_blocks){
              void** memory_to_free = dynamically_allocated_memory + i;
              free(*memory_to_free);
              i++;
          }

          dynamic_blocks = 0;
          i = 0;
          while (i < total_words){
              char** word_to_free = words + i;
              free(*word_to_free);
              i++;
          }
        
          i = 0;
          while (i < num_words_played){
              char** word_played_to_free = words_played + i;
              free(*word_played_to_free);
              i++;
          }
          //free all =here
          free(words);
          free(words_played);
          free(tids);
          free(dynamically_allocated_memory);
          free(server_fds);     
          exit(1);
      }
  }
}

char* under(char* s){
    int temp = strlen(s) + 1;
    char* ret = allocation(temp, 1);
    for(int i = 0;i<strlen(s);i++){
        *(ret+i) = tolower(*(s+i));
    }
    return ret;
}
char* under2(char* s){
    int temp = strlen(s) + 1;
    char* ret = calloc(temp, 1);
    for(int i = 0;i<strlen(s);i++){
        *(ret+i) = tolower(*(s+i));
    }
    return ret;
}

int good_guess(char* guess){
    if (strlen(guess) == 5){
        //continue;
    } else{
        return 0;
    }
    for(int i = 0;i<total_words;i++){
        if(strcmp(guess, *(words+i)) == 0){
            return 1;
        }
    }
    return 0;
}

char* check_match(char* word, char* guess){
    int five = 5;
    char* ret = allocation(five, 1);
    memcpy(ret, "-----", five);
    for(int i = 0;i<5;i++){
        if(*(word+i) == *(guess+i)){
            *(ret+i) = toupper(*(word+i));
        }
    }
    
    for(int i=0;i<five;i++){
        if(*(ret+i) == '-'){
            for(int j = 0;j<five;j++){
                if(*(word+j) == *(guess+i)){
                    *(ret+i) = *(guess+i);
                    break;
                }
            }
        }
    }
    return ret;
}

int check_win(char* match_str){
    for(int i = 0;i<5;i++){
        if(!isupper(*(match_str+i))){
            return 0;
        }
    }
    return 1;
}


ssize_t send_message(int socket_fd, const char *message) {
    return send(socket_fd, message, strlen(message), 0);
}

ssize_t recv_message(int socket_fd, char *buffer, size_t buffer_size) {
    ssize_t bytes_read = recv(socket_fd, buffer, buffer_size, 0);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';  
    }
    return bytes_read;
}


void * make_game_server( void * arg ){
   int newsd = *((int*)arg);

   char* word = *(words + rand() % total_words);
   pthread_mutex_lock(&mutex);

   words_played = realloc(words_played, sizeof(char*) * (num_words_played + 1));

   char** new_word_location = words_played + num_words_played;

   *new_word_location = calloc(6, 1);

   strcpy(*new_word_location, word);

   num_words_played++;
   
   pthread_mutex_unlock(&mutex);
   int n;
   short guesses_remaining = 6;
   do {
     char* buffer = allocation(MAXBUFFER+1, 1);

     printf("THREAD %ld: waiting for guess\n", pthread_self());   
     n = recv( newsd, buffer, MAXBUFFER, 0 );

     
     if ( n == 0 )   {
       printf("THREAD %ld: client gave up; closing TCP connection...\n", pthread_self() );
       char* won_str = upper(word);
       printf("THREAD %ld: game over; word was %s!\n", pthread_self(), won_str); 
       pthread_mutex_lock(&mutex);
       {
           total_losses++;
       }
       pthread_mutex_unlock(&mutex);
       break;
       
     }
     else if ( n == -1 ) {
        perror( "ERROR: recv() failed" );
       return NULL;
       
     }
     else  { 
        int bytes_read = n;
        while (bytes_read < 5) {
            bytes_read += recv(newsd, buffer + bytes_read, MAXBUFFER - bytes_read, 0);
        }
        *(buffer + bytes_read) = '\0';  
        char* response = allocation(9, 1);

        char* undered = under(buffer);
        printf("THREAD %ld: rcvd guess: %s\n", pthread_self(), undered);

        int is_valid = good_guess(undered); 
        int won = 0;
        if (is_valid) {
            *response = 'Y';
            guesses_remaining--;

            char* match_str = check_match(word, undered);

            won = check_win(match_str);
            memcpy(response + 3, match_str, 5);
            short guesses_left_n = htons(guesses_remaining);
            memcpy(response + 1, &guesses_left_n, 2);
            printf("THREAD %ld: sending reply: %s (%d guess%s left)\n", pthread_self(), response + 3, guesses_remaining, guesses_remaining != 1 ? "es" : "");
            pthread_mutex_lock(&mutex);
            total_guesses++;
            pthread_mutex_unlock(&mutex);
        } else {
            *response = 'N';
            memcpy(response + 3, "?????", 5);
            short guesses_left_n = htons(guesses_remaining);
            memcpy(response + 1, &guesses_left_n, 2);
            printf("THREAD %ld: invalid guess; sending reply: %s (%d guess%s left)\n", pthread_self(), response + 3, guesses_remaining, guesses_remaining != 1 ? "es" : "");
        }
        n = send(newsd, response, 8, 0);
        if (n == -1) {
            perror("ERROR: send() failed"); 
            pthread_detach(pthread_self()); 
            return NULL;
        }
        if (won) {
            char* won_str = upper(word);
            printf("THREAD %ld: game over; word was %s!\n", pthread_self(), won_str); 
            pthread_mutex_lock(&mutex);
            total_wins++;
            pthread_mutex_unlock(&mutex);
            break;
        }
        if (guesses_remaining == 0) {
            char* won_str = upper(word);
            printf("THREAD %ld: game over; word was %s!\n", pthread_self(), won_str); 
            pthread_mutex_lock(&mutex);
            total_losses++;
            pthread_mutex_unlock(&mutex);
            break;
        }
 
     }
   }
   while(1);
   pthread_mutex_lock(&mutex);
   {
       pthread_detach_and_save(pthread_self());
    
        close(newsd);
        int i = 0;
        while (i < servers){
            if(*(server_fds+i) == newsd){
        
                for(int j = i+1;j<servers;j++){
                    *(server_fds+j-1) = *(server_fds+j);
                }
                servers = servers  - 1;
                break;
            }
            i++;
        }
        server_fds = realloc(server_fds, sizeof(int)*servers);
   }
   pthread_mutex_unlock(&mutex);
   return NULL;
}


int wordle_server(int argc, char** argv){
    if(argc != 5){
        fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: hw4.out <received-port> <seed> <word-filename> <num-words>");
        return EXIT_FAILURE;
    }
    short tcp_received_port = (short)strtol(*(argv+1), NULL, 10);
    if(tcp_received_port < 0){
        perror("ERROR: tcp_received_port should be >= 0");
        return EXIT_FAILURE;
    }

    int iter = 2;
    int seedtotal = 10;
    int seed = (int)strtol(*(argv + iter), NULL, seedtotal);
    iter++; 
    char* words_filename = *(argv + iter);
    iter++;
    int file_words = (int)strtol(*(argv + iter), NULL, seedtotal);
    srand(seed);
    words = realloc(words, sizeof(char*) * (file_words + 1));
    *(words + file_words) = NULL;
    FILE* fp = fopen(words_filename, "r");
    if (fp == NULL) {
        perror("ERROR: fopen() failed");
        return EXIT_FAILURE;
    }

    ssize_t read;
    char* buffer = NULL;
    int i = 0;
    size_t len = 0;
    while ((read = getline(&buffer, &len, fp)) != -1) {
        *(words + i) = calloc(1, 6);
        char* undered = under2(buffer);
        strncpy(*(words + i), undered, 5);
        free(undered);
        i++;
    }

    parent_thread = pthread_self();
    signal(SIGINT, SIG_IGN);    
    signal(SIGTERM, SIG_IGN);    
    signal(SIGUSR2, SIG_IGN);    
    signal(SIGUSR1, signal_handler);
    free(buffer);
    fclose(fp);
    printf("MAIN: opened %s (%d words)\n", words_filename, file_words);
    total_words = file_words;

    received = socket(AF_INET, SOCK_STREAM, 0);

    if (received == -1) {
        perror("ERROR: socket() failed");
        return EXIT_FAILURE;
    }

    struct sockaddr_in tcp_server;
    tcp_server.sin_family = AF_INET;
    tcp_server.sin_addr.s_addr = htonl(INADDR_ANY);
    tcp_server.sin_port = htons(tcp_received_port);

    if (bind(received, (struct sockaddr *) &tcp_server, sizeof(tcp_server)) == -1) {
        perror("ERROR: bind() failed");
        return EXIT_FAILURE;
    }

    if (listen(received, 5) == -1) {
        perror("ERROR: listen() failed");
        return EXIT_FAILURE;
    }

    printf("MAIN: Wordle server listening on port {%d}\n", tcp_received_port);

    while (1 == 1){
      struct sockaddr_in remote_client;
      int addrlen = sizeof( remote_client );
  
      int* server_ptr = allocation(1, sizeof(int));
      *server_ptr = accept_and_save( received, (struct sockaddr *)&remote_client,
                          (socklen_t *)&addrlen );
      if ( *server_ptr == -1 ){ 
        perror( "ERROR: accept() failed" ); 
        continue; 
      }
      printf("MAIN: rcvd incoming connection request\n");
 
      int rc = pthread_allocation(NULL, make_game_server, server_ptr);
      if(rc == -1){
          perror("ERROR: pthread_create() failed");
          return EXIT_FAILURE;
      }
  
    }
    return EXIT_SUCCESS;
}


