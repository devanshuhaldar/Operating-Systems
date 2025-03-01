// // #include <stdio.h>
// // #include <stdlib.h>
// // #include <string.h>
// // #include <unistd.h>
// // int main()
// // {
// // char * a = "POLYTECHNIC";
// // char * b = a;
// // char * c = calloc( 100, sizeof(int)  );
// // printf( "[%s][%s][%s]\n", a + 10, b + 9, c + 8 );
// // char ** d = calloc( 100 , sizeof(int));
// // d[7] = calloc( 20, sizeof(int) );
// // d[6] = c;
// // strcpy( d[7], b + 5 );
// // strcpy( d[6], b + 4 );
// // printf( "[%s][%s][%s]\n", d[7], d[6], c + 5 );
// // float e = 2.71828;
// // float * f = calloc( 1 , sizeof(int) );
// // float * g = f;
// // float * h = &e;
// // printf( "[%3.2f][%2.2f][%2.1f]\n", *f, *g, *h );
// // return EXIT_SUCCESS;
// // }


// // #include <stdio.h>
// // #include <stdlib.h>
// // #include <unistd.h>
// // int main()
// // {
// //     printf( "ONE\n" );
// //     fprintf( stderr, "ERROR: ONE\n" );
// //     int rc = close( 2 );
// //     printf( "==> %d\n", rc );
// //     printf( "TWO\n" );
// //     fprintf( stderr, "ERROR: TWO\n" );
// //     rc = dup2( 1 , 2 );
// //     printf( "==> %d\n", rc );
// //     printf( "THREE\n" );
// //     fprintf( stderr, "ERROR: THREE\n" );
// //     return EXIT_SUCCESS;
// // }



// // #include <stdio.h>
// // #include <stdlib.h>
// // #include <unistd.h>
// // #include <fcntl.h>
// // int main()
// // {
// // int fd;
// // close( 2 );
// // printf( "HI\n" );
// // // #if 0
// // close( 1 ); /* <== add this line later.... */
// // // #endif
// // fd = open( "output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0600 );

// // printf( "==> %d\n", fd );
// // printf( "WHAT?\n" );
// // fprintf( stderr, "ERROR\n" );
// // close( fd );
// // return EXIT_SUCCESS;
// // }



// // #include <stdio.h>
// // #include <stdlib.h>
// // #include <unistd.h>
// // #include <fcntl.h>
// // #include <sys/wait.h>
// // int main(){
// // int fd;
// // close( 2 );
// // printf( "HI\n" );
// // #if 0
// // close( 1 ); /* <== add this line later.... */
// // #endif
// // fd = open( "output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0600 );
// // printf( "==> %d\n", fd );
// // printf( "WHAT?\n" );
// // fprintf( stderr, "ERROR\n" );

// // int rc = fork();
// // if ( rc == 0 ) {
// // printf( "AGAIN?\n" );
// // fprintf( stderr, "ERROR ERROR\n" );
// // }else{
// // waitpid( -1, NULL, 0 );
// // }
// // printf( "BYE\n" );
// // fprintf( stderr, "HELLO\n" );
// // close( fd );
// // return EXIT_SUCCESS;
// // }





// #include <stdio.h>
// #include <stdlib.h>
// #include <unistd.h>
// int main()
// {
// int rc;
// int p[2];
// rc = pipe( p );
// printf( "%d %d %d\n", getpid(), p[0], p[1] );
// rc = fork();
// if ( rc == 0 )
// {
// rc = write( p[1], "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 26 );
// }
// if ( rc > 0 )
// {
// char buffer[70];
// rc = read( p[0], buffer, 8 );
// buffer[rc] = '\0';
// printf( "%d %s\n", getpid(), buffer );
// }
// printf( "BYE\n" );
// return EXIT_SUCCESS;
// }


// // #include <stdio.h>
// // #include <stdlib.h>
// // #include <unistd.h>

// // int main() {
// //     // Open a file for writing
// //     FILE *file = fopen("block_buffer_example.txt", "w");

// //     if (file == NULL) {
// //         perror("Error opening file");
// //         return 1;
// //     }

// //     // Set up block buffering with a buffer size of 4096 bytes
// //     char buffer[4096];
// //     if (setvbuf(file, buffer, _IOFBF, sizeof(buffer)) != 0) {
// //         perror("Error setting buffer");
// //         return 1;
// //     }
// //     printf("hello there!");
// //     // Fork a child process
// //     pid_t child_pid = fork();

// //     if (child_pid == -1) {
// //         perror("Error forking");
// //         return 1;
// //     }

// //     if (child_pid == 0) {
// //         // Child process
// //         printf("Child process writing to file.\n");
// //         for (int i = 1; i <= 2; ++i) {
// //             fprintf(file, "Child Line %d: This is some data\n", i);
// //         }
// //         printf("Child process completed.\n");
// //         // exit(0);
// //     } else {
// //         // Parent process
// //         printf("Parent process writing to file.\n");
// //         for (int i = 1; i <= 2; ++i) {
// //             fprintf(file, "Parent Line %d: This is some data\n", i);
// //         }
// //         printf("Parent process completed.\n");

// //         // Wait for the child to complete
// //         wait(NULL);
// //     }

// //     // Close the file
// //     printf("adios");
// //     fclose(file);

// //     return 0;
// // }

#include <stdio.h>      // For fprintf, setvbuf
#include <stdlib.h>     // For exit() function, if needed
#include <fcntl.h>      // For open() function constants
#include <unistd.h>     // For close() function

int main() {
    printf("Hi");
    fork();
}
