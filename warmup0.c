// /* be-careful.c */

// /* Be sure to allocate space for the '\0' character when
//     treating data as a printable character string! */

// /* Fix the warnings shown when you compile as follows:
//  *
//  * bash$ gcc -Wall -Werror be-careful.c
//  *
//  */

// #include <stdio.h>
// #include <stdlib.h>
// #include <unistd.h>
// #include <string.h>

// int main()
// {
// #if 0
//   /* we will go over this on Friday 1/12 */
//   char * x = "ABCD";  /* note that *x points to read-only memory */
//   x[2] = 'Q';  /* this will seg-fault */
// #endif

//   char name[3] = "Wes";      /* Wes\0" */
//   printf( "hi %s\n", name );   /*  ^^ this is one character/byte */

//   name[1] = 'x';
//   printf( "hi %s\n", name );

//   char xyz[5] = "QRSTU";
//   printf( "hi again %s\n", name );   /* why does this output "WxsQRSTU" ?! */

//   char * path = malloc( 20 );
//   strcpy( path, "/cs/wdturner/s24/os" );
//   printf( "path is %s\n", path );

//   char * path2 = malloc( 20 );
//   strcpy( path2, "/cs/wdturner/24/os" );
//   printf( "path2 is %s\n", path2 );
  
//   /* the next string is more than the allocated 20 bytes... */
//   strcpy( path, "/cs/wdturner/24/os/blah/blah/blah/meme" );
//   printf( "path is %s\n", path );

//   printf( "path2 is %s\n", path2 );  /* what does this line output? why?! */
//   printf( "path2[8] is %c\n", path2[8] );  /* what does this line output? why?! */

//   free( path );
//   free( path2 );   /* why does this seg-fault? */

//   return EXIT_SUCCESS;
//  }







// #include <stdio.h>
// #include <stdlib.h>
// #include <unistd.h>

// int main()
// {
// 	int x = 42;
// 	int *y = NULL;
// 	y = &x;
// 	printf("x = %d\n", x);
// 	printf("y = 0x%x\n", *y);

// 	printf("size int = %ld\n", sizeof(x));
// 	printf("size int * = %ld\n", sizeof(y));
// 	printf("size void * = %ld\n", sizeof(void *));
// 	printf("size float * = %ld\n", sizeof(float *));
// 	printf("size float = %ld\n", sizeof(float));
// 	printf("size long = %ld\n", sizeof(long));
// 	return EXIT_SUCCESS;
// }



#include <stdio.h>

#define CACHE_SIZE 47

// Function to calculate the sum of 1 to N
long long calculateSum(int N) {
    long long sum = 0;
    for (int i = 1; i <= N; i++) {
        sum += i;
    }
    return sum;
}

// Function to check if a value is present in the cache
int isInCache(int cache[], int size, int key) {
    for (int i = 0; i < size; i++) {
        if (cache[i] == key) {
            return 1; // Value found in cache
        }
    }
    return 0; // Value not found in cache
}

// Function to update the cache with a new value
void updateCache(int cache[], int size, int key) {
    // Shift elements to make space for the new value
    for (int i = size - 1; i > 0; i--) {
        cache[i] = cache[i - 1];
    }
    // Insert the new value at the beginning of the cache
    cache[0] = key;
}

int main() {
    int cache[CACHE_SIZE] = {0}; // Initialize cache with zeros
    int userInput;

    while (1) {
        // Ask the user to input an integer
        printf("Enter an integer (0 to exit): ");
        scanf("%d", &userInput);

        if (userInput == 0) {
            break; // Exit the program if the user inputs 0
        }

        // Check if the value is already in the cache
        if (isInCache(cache, CACHE_SIZE, userInput)) {
            printf("Result from cache: %d\n", userInput);
        } else {
            // Calculate the sum and update the cache
            long long result = calculateSum(userInput);
            printf("Calculated result: %lld\n", result);
            updateCache(cache, CACHE_SIZE, userInput);
        }
    }

    return 0;
}
