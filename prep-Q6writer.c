/* prep-Q6writer.c */

/* Create a shared memory segment with a known key and a size of 64 bytes.
 *  Next, have this program prompt the user to repeatedly enter a line
 *   of text.  Each line is written to the shared memory segment,
 *    truncating the line to fit, if necessary.
 *
 * The synchronization protocol will be implemented in the first byte
 *  of the shared memory segment as follows: s
 *
 *   'W' -- write mode in which this process is writing data
 *           (no reads should occur)
 *
 *   'R' -- read mode in which the other process is reading data
 *           (no writes should occur)
 *
 *   'D' -- detach mode in which both processes should detach
 *           from the shared memory segment
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <sys/wait.h>

/* This constant defines the shared memory segment key
 *  such that multiple processes can attach to this segment */
#define SHM_SHARED_KEY 8192

/* This constant defines the size of the shared memory segment */
#define SHM_SIZE 64

/* This constant defines the size of the input buffer,
 *  which must be one byte smaller than SHM_SIZE to
 *   account for the synchronization protocol above */
#define BUFFER_SIZE ( SHM_SIZE - 1 )

int main()
{
  /* create the shared memory segment with a size of 128 bytes */
  key_t key = SHM_SHARED_KEY;
  int shmid = shmget( key, SHM_SIZE, IPC_CREAT | /* IPC_EXCL | */ 0660 );
  if ( shmid == -1 ) { perror( "shmget() failed" ); return EXIT_FAILURE; }

  /* attach to the shared memory segment */
  char * data = shmat( shmid, NULL, 0 );
  if ( data == (char *)-1 ) { perror( "shmat() failed" ); return EXIT_FAILURE; }

  data[0] = 'W';  /* initially in a write (W) mode */

  while ( 1 )
  {
    char buffer[BUFFER_SIZE];
    printf( "Enter data (CTRL-D to exit) ==> " );
    fflush( stdout );

    if ( fgets( buffer, BUFFER_SIZE, stdin ) == NULL ) break;
      /*                ^^^^^^^^^^^                         */
      /* note that BUFFER_SIZE is 63 and fgets() will read  */
      /*  then at most 62 bytes (to leave room for '\0')... */

    int len = strlen( buffer );
    if ( len <= 1 ) continue;   /* skip blank lines */

    /* truncate the rest of the input line */
    if ( buffer[len-1] != '\n' ) while ( fgetc( stdin ) != '\n' );

    /* replace trailing newlines with '\0' characters... */
    while ( buffer[len-1] == '\n' ) buffer[--len] = '\0';

    strcpy( data + 1, buffer );

    data[0] = 'R';  /* set to read (R) mode */

    while ( data[0] == 'R' ) /* busy wait */ usleep( 100 );
  }

  data[0] = 'D';  /* set to detach (D) mode */
  printf( "\n" );

  /* detach from the shared memory segment */
  int rc = shmdt( data );
  if ( rc == -1 ) { perror( "shmdt() failed" ); exit( EXIT_FAILURE ); }

  /* remove the shared memory segment */
  if ( shmctl( shmid, IPC_RMID, 0 ) == -1 ) { perror( "shmctl() failed" ); exit( EXIT_FAILURE ); }

  return EXIT_SUCCESS;
}
