// /* count-shm-mutex.c */

// #include <stdio.h>
// #include <stdlib.h>
// #include <sys/wait.h>
// #include <unistd.h>
// #include <errno.h>
// #include <time.h>
// #include <string.h>
// #include <ctype.h>
// #include <sys/ipc.h>
// #include <sys/shm.h>
// #include <pthread.h>

// /* This constant defines the shared memory segment such that
//    multiple processes can attach to this segment */
// #define SHM_SHARED_KEY 8999

// typedef struct
// {
//     long data;
//     pthread_mutex_t lock;
// } shared_data;

// int main()
// {
//   /* create the shared memory segment with a size of 4 bytes */
//   key_t key = SHM_SHARED_KEY;
//   int shmid = shmget( key, sizeof( shared_data ), IPC_CREAT | /*IPC_EXCL |*/ 0660 );
//   printf( "shmget() returned %d\n", shmid );

//   if ( shmid == -1 )
//   {
//     perror( "shmget() failed" );
//     return EXIT_FAILURE;
//   }

//   /* attach to the shared memory segment */
//   shared_data * data = shmat( shmid, NULL, 0 );
//   if ( data == (shared_data *)-1 )
//   {
//     perror( "shmat() failed" );
//     return EXIT_FAILURE;
//   }

//   data->data = 0;

//   /*
//    * All of this is just because we are using processes.
//    *          VVVVVVVVVVVVVVVVVVVVVVV
//    */
//   int rc;
//   pthread_mutexattr_t attr;
//   rc = pthread_mutexattr_init(&attr);
//   if (rc != 0)
//   {
//     fprintf(stderr, "pthread_mutexattr_init() error: %d\n", rc);
//   }
//   rc = pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
//   if (rc != 0)
//   {
//     fprintf(stderr, "pthread_mutexattr_setpshared() error: %d\n", rc);
//   }
//   rc = pthread_mutex_init(&data->lock, &attr);
//   if (rc != 0)
//   {
//     fprintf(stderr, "pthread_mutexattr_setpshared() error: %d\n", rc);
//   }
//   /*
//    * ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//    */
  
//   int pid = fork();

//   if (pid > 0) usleep(100);

//   /* Both run this code. */
//   for (int ctr=1; ctr <= 1000000; ctr++)
//   {
//       // Put in the mutual exclusion here VVVV
//       pthread_mutex_lock(&data->lock);
// 	  data->data += ctr; /* this is the same as data = data + ctr*/
//       pthread_mutex_unlock(&data->lock);
//       // ^^^^ Is the critical section
//   }

//   printf("%s: Sum 1 ... 1000000 is %ld\n", pid > 0 ? "Parent" : "Child", data->data);

//   if (pid > 0)
//   {
//     waitpid(pid, NULL, 0);
//     printf("%s: Sum 1 ... 1000000 is %ld\n", pid > 0 ? "Parent" : "Child", data->data);
//   }

//   rc = shmdt( data );

//   if ( rc == -1 )
//   {
//     perror( "shmdt() failed" );
//     exit( EXIT_FAILURE );
//   }

// #if 1
//   if ( pid > 0 )   /* skip this and see what happens */
//   {
//     wait( NULL );
//                          /* remove the shared memory segment */
//     if ( shmctl( shmid, IPC_RMID, 0 ) == -1 )
//     {
//       perror( "shmctl() failed" );
//       exit( EXIT_FAILURE );
//     }
//   }
// #endif


//   return EXIT_SUCCESS;
// }
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#define SONNY 1
void * wtf( void * arg )
{
    int * f = (int *)arg;
    printf( "%ldA%d\n", pthread_self(), *f );
    fprintf( stderr, "%ldB\n", pthread_self() );
    return NULL;
}
int main()
{
    close( SONNY );
    printf( "%ldC\n", pthread_self() );
    fprintf( stderr, "%ldD\n", pthread_self() );
    int fd = open( "E.txt", O_WRONLY | O_CREAT | O_TRUNC, 0660 );
    printf( "%ldF\n", pthread_self() );
    fprintf( stderr, "%ldG%d\n", pthread_self(), fd );
    pthread_t tid1, tid2;
    int rc = pthread_create( &tid1, NULL, wtf, &fd );
    rc = pthread_create( &tid2, NULL, wtf, &rc );
    pthread_join( tid1, NULL );
    pthread_join( tid2, NULL );
    printf( "%ldH\n", pthread_self() );
    fprintf( stderr, "%ldI\n", pthread_self() );
    fflush( NULL );
    close( fd );
    return EXIT_SUCCESS;
}
