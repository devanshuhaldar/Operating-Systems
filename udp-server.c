/* udp-server.c */

/* To test this server, you can use the following
   command-line netcat tool:

   bash$ netcat -u linux00.cs.rpi.edu 41234
         ^^^^^^
      in this case, netcat will act as a client to
       this UDP server....

   The hostname (e.g., linux00.cs.rpi.edu) cannot be
   localhost (127.0.0.1); and the port number must match what
   the server reports.

*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#define MAXBUFFER 8192

int main()
{
  //
  // We need to create a socket to wait for communication requests. 
  // A socket requires a host address, and it requires a port number.
  // The following code creates a UDP socket on the host (... with the IP
  // address of this host), and then "names" or "binds" it to a specific 
  // port.
  // 

  int sd = socket(AF_INET, SOCK_DGRAM, 0); // Create a socket at our IP address.
  if (sd == -1)
  {
    perror("socket() failed: ");
    return EXIT_FAILURE;
  }
  printf("Socket: %d\n", sd);

  struct sockaddr_in server;
  
  server.sin_family = AF_INET;
  server.sin_port = htons(0);
  server.sin_addr.s_addr = htonl( INADDR_ANY );

  if (bind(sd, (struct sockaddr *) &server, sizeof(server)) < 0)
  {
    perror("bind() failed: ");
    return EXIT_FAILURE;
  }

  socklen_t length = sizeof(server);
 /* call getsockname() to obtain the port number that was just assigned */
  if ( getsockname( sd, (struct sockaddr *) &server, (socklen_t *) &length ) < 0 )
  {
    perror( "getsockname() failed" );
    return EXIT_FAILURE;
  }

  printf("Bound to port %d\n", ntohs(server.sin_port));

  int n;
  char buffer[MAXBUFFER + 1];
  struct sockaddr_in client;
  
  while ( 1 )
  {
    //
    // Once the socket is created correctly, we can use it to communicate ...
    //
#if 0
    n = read( sd, buffer, MAXBUFFER);
    if (n == -1)
    {
      perror("read() failed: ");
      return EXIT_FAILURE;
    }
    printf("Received %d bytes.\n", n);
    buffer[n] = '\0';   // Terminate our string.
    printf("Received string [%s].\n", buffer);
    
#endif
#if 1
    unsigned len = sizeof(client);
    n = recvfrom( sd, buffer, MAXBUFFER, 0, (struct sockaddr *) &client, &len);
    if (n == -1)
    {
      perror("read() failed: ");
      return EXIT_FAILURE;
    }

    printf("Received %d bytes from %s port %d.\n", n, inet_ntoa(client.sin_addr), ntohs(client.sin_port));
    buffer[n] = '\0';   // Terminate our string.
    printf("Received string [%s].\n", buffer);
 #endif   

    sendto(sd, buffer, n, 0, (struct sockaddr *) &client, len);
  }

  return EXIT_SUCCESS;
}
