#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <CommonCrypto/CommonDigest.h>
#include <omp.h>
#include <string.h>
#include <time.h>
//#include <openssl/sha.h>

//appendable characters
static const char* alphanums = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

//
// Mapping from 6 bit pattern to ASCII character.
//
static unsigned char base64EncodeLookup[65] =
"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

//
// Fundamental sizes of the binary and base64 encode/decode units in bytes
//
#define BINARY_UNIT_SIZE 3
#define BASE64_UNIT_SIZE 4

#define MAX_NUM_PADDING_CHARS 2
#define OUTPUT_LINE_LENGTH 64
#define INPUT_LINE_LENGTH ((OUTPUT_LINE_LENGTH / BASE64_UNIT_SIZE) * BINARY_UNIT_SIZE)
#define CR_LF_SIZE 2

//
// NewBase64Encode
//
// Encodes the arbitrary data in the inputBuffer as base64 into a newly malloced
// output buffer.
//
//  inputBuffer - the source data for the encode
//	length - the length of the input in bytes
//  separateLines - if zero, no CR/LF characters will be added. Otherwise
//		a CR/LF pair will be added every 64 encoded chars.
//	outputLength - if not-NULL, on output will contain the encoded length
//		(not including terminating 0 char)
//
// returns the encoded buffer. 
//
void NewBase64Encode(const void *buffer, size_t length, int separateLines, size_t *outputLength , char *outputBuffer)
{
	const unsigned char *inputBuffer = (const unsigned char *)buffer;
	
	size_t i = 0;
	size_t j = 0;
	const size_t lineLength = separateLines ? INPUT_LINE_LENGTH : length;
	size_t lineEnd = lineLength;
	
	while (1)
	{
		if (lineEnd > length)
		{
			lineEnd = length;
		}
		
		for (; i + BINARY_UNIT_SIZE - 1 < lineEnd; i += BINARY_UNIT_SIZE)
		{
			//
			// Inner loop: turn 48 bytes into 64 base64 characters
			//
			outputBuffer[j++] = base64EncodeLookup[(inputBuffer[i] & 0xFC) >> 2];
			outputBuffer[j++] = base64EncodeLookup[((inputBuffer[i] & 0x03) << 4)
												   | ((inputBuffer[i + 1] & 0xF0) >> 4)];
			outputBuffer[j++] = base64EncodeLookup[((inputBuffer[i + 1] & 0x0F) << 2)
												   | ((inputBuffer[i + 2] & 0xC0) >> 6)];
			outputBuffer[j++] = base64EncodeLookup[inputBuffer[i + 2] & 0x3F];
		}
		
		if (lineEnd == length)
		{
			break;
		}
		
		//
		// Add the newline
		//
		outputBuffer[j++] = '\r';
		outputBuffer[j++] = '\n';
		lineEnd += lineLength;
	}
	
	if (i + 1 < length)
	{
		//
		// Handle the single '=' case
		//
		outputBuffer[j++] = base64EncodeLookup[(inputBuffer[i] & 0xFC) >> 2];
		outputBuffer[j++] = base64EncodeLookup[((inputBuffer[i] & 0x03) << 4)
											   | ((inputBuffer[i + 1] & 0xF0) >> 4)];
		outputBuffer[j++] = base64EncodeLookup[(inputBuffer[i + 1] & 0x0F) << 2];
		outputBuffer[j++] =	'=';
	}
	else if (i < length)
	{
		//
		// Handle the double '=' case
		//
		outputBuffer[j++] = base64EncodeLookup[(inputBuffer[i] & 0xFC) >> 2];
		outputBuffer[j++] = base64EncodeLookup[(inputBuffer[i] & 0x03) << 4];
		outputBuffer[j++] = '=';
		outputBuffer[j++] = '=';
	}
	outputBuffer[j] = 0;
	
	//
	// Set the output length and return the buffer
	//
	if (outputLength)
	{
		*outputLength = j;
	}
	
}

/*
 * Validates inputs and exits if they do not match requirements.
 */
void validate(const char* short_tag, const char* prefix, const int suffix_size, int num_tags, const int threads) {
	
	if (strlen(short_tag) < 1) {
		
		printf("Short tag must be at least 1 character long.");
		exit(1);
	}
	
	if(strlen(prefix) < 1) {
		
		printf("Prefix must be atleast 1 character long");
		exit(1);
	}
	
	if (suffix_size < 1) {
		
		printf("Suffix size must be greater than or equal to 1");
		exit(1);
	}
	
	if (num_tags < 1 && num_tags != -1) {
		
		printf("Num tags must be greater than or equal to 1, or equal to -1 for all matches");
		exit(1);
	}
	
	if (threads < 1) {
		
		printf("Threads must be greater than or equal to 1");
		exit(1);
	}
}

/*
 *	Creates an array of size num_digits padded with zeros and fills in the digits of num converted
 *  to output_base. A pointer to the array is assigned to result_buffer; 
 */
void baseConverter(unsigned long long num, int output_base, int num_digits, int** result_buffer) {
	
	int* buffer = malloc(num_digits * sizeof(int));
	unsigned long long M = num;
	int offset = 0;
	
	//pad out buffer with zeros
	for(int i = 0; i < num_digits; i++)
		buffer[i] = 0;
	
	//convert input into base output_base form
	while (M >= (unsigned long long)output_base) {
		
		int temp = M % output_base;
		buffer[num_digits - offset - 1] = temp;
		M = M/output_base;
		offset++;
		
		if(offset > num_digits) {
			
			printf("Entered number that exceeded number of digits allowable for num %llu, digits %d", num, num_digits);
			exit(1);
		}
	}
	
	buffer[0] = M;
	
	*result_buffer = buffer;
}

/*
 * Increments the array of digits in base -base- by 1, updating subsequent digits if necessary. Will overflow 
 * if incremented beyond base ^ num_digits - 1, but this is a desired property
 */
void baseIncrementer(int* num, int base, int num_digits) {
	
	for (int i = num_digits -1; i >= 0; i--) {
		
		if(num[i] == (base - 1)) {
			
			num[i] = 0;
		}
		else {
			
			num[i]++;
			break;
		}
	}
}

/*
 *	Returns an int array of size num_threads containing as close to evenly divided
 *	chunks of the exploration_space_size. This allows any thread to start executing
 *	from any position in the exploration space and execute from start to 
 *  start + iterationChunks[thread_num] - 1 without overlapping other threads. 
 *
 */
unsigned long long* getIterationChunks(unsigned long long exploration_space_size, int num_threads) {
	
	unsigned long long exploration_chunks = (unsigned long long) exploration_space_size / num_threads;
	int exploration_chunks_remainder = (int)(exploration_space_size % num_threads);
	
	unsigned long long* iterationChunks = malloc(num_threads * sizeof(unsigned long long));
	
	for( int i = 0; i < num_threads; i++ ) {
		iterationChunks[i] = exploration_chunks;
        
        if( exploration_chunks_remainder != 0 ) {
            iterationChunks[i]++;
            exploration_chunks_remainder--;
        }
    }
	
	return iterationChunks;
}

/*
 * usage: ./collider short_tag prefix suffix_size num_tags threads
 *
 * find num_tags collisions with short_tag by appending suffix_size characters to prefix. Use threads
 * number of threads to compute this.
 */
int main(int argc, char *argv[])
{	
	const char *short_tag = argv[1];
	const char *prefix = argv[2];
	const int suffix_size = atoi(argv[3]);
	int num_tags = atoi(argv[4]);
    const int s_num_tags = num_tags;
	const int threads = atoi(argv[5]);
	
	validate(short_tag, prefix, suffix_size, num_tags, threads);
	
	omp_set_num_threads(threads);
	
	//get the length of the printiable chars string, this becomes the base for the exploration space
	const int alphanumLen = strlen(alphanums);
	const unsigned long long exploration_space_size = (unsigned long long)pow(alphanumLen, suffix_size);
	
	// Byte accurate calculation of final buffer size
	size_t long_tag_encoded_size = ((20 / BINARY_UNIT_SIZE) + ((20 % BINARY_UNIT_SIZE) ? 1 : 0)) * BASE64_UNIT_SIZE;
	
	// Include space for a terminating zero
	long_tag_encoded_size += 1;
	
	//seed the random generator and use it to give a random starting position
	//since exploration space is a long long and rand returns an in, use bit
	//shifting to fill in a truly pseudo random start pos.
	int time_seed = time(NULL);
	srand(time_seed);
	double factor = (double)sizeof(long long) / sizeof(int);
	if (factor != 2) {
		
		printf("Error, long long is not twice the size of int as expected.");
		exit(1);
	}
	unsigned long long startPos = rand();
	startPos <<= sizeof(int);
	startPos += rand();
    startPos = startPos % exploration_space_size;
	
	//divide the space up into approximately equal chunks based on number of threads
	unsigned long long* iterationChunks = getIterationChunks(exploration_space_size, threads);
	
	const int shortTagLen = strlen(short_tag);
	const int prefixLen = strlen(prefix);
	unsigned long long tags_checked = 0;
	unsigned long long tags_found = 0;
	
	#pragma omp parallel for default(none) \
	firstprivate(long_tag_encoded_size, startPos, iterationChunks, prefix, alphanums, short_tag) \
	shared(num_tags) \
	reduction(+: tags_checked, tags_found)
	for (int i = 0; i < threads; i++)
	{	
		//plain tag buffer, must accomodate prefix and suffix plus null terminator
		unsigned char plain_tag[prefixLen + suffix_size + 1];
		strncpy((char*)plain_tag, prefix, prefixLen);
		
		//buffer for sha1 hash
		unsigned char long_tag[20];
		
		//buffer for base 64 of sha1 hash
		char long_tag_encoded[long_tag_encoded_size];
		
		//compute the start position by advancing the start index by chunks
		unsigned long long start = startPos;

		for (int j = 0; j < threads; j++) {
			
			//if the chunk matches the thread num, we'e advanced enough
			if (j == i) {
				break;
			}
			else {
				
				start += iterationChunks[j];
				start = start % exploration_space_size;
			}
		}
		
		int* suffix_rep;
		
		//initializes the character representation in base 64
		baseConverter(start, alphanumLen, suffix_size, &suffix_rep);
		
		unsigned long long index = 0;
		unsigned long long numIterations = iterationChunks[i];
		
		while((num_tags > 0 || s_num_tags == -1) && index < numIterations)
		{
			
			// Generate random string by using the suffix_rep digits as lookups into
			//the alphanums string of printable chars.
			for (int a = 0; a < suffix_size; a++) 
			{
		        plain_tag[prefixLen + a] = (unsigned char)alphanums[suffix_rep[a]];
		    }
			
		    plain_tag[prefixLen + suffix_size] = '\0';
			
			CC_SHA1(plain_tag, prefixLen + suffix_size, long_tag);
			//SHA1(plain_tag, prefixLen + suffix_size, long_tag);
			
			NewBase64Encode(long_tag, 20, 0, NULL, long_tag_encoded);
			
			// Compares the input short tag to the long tag truncated to the length of the short tag
			if (strncmp(short_tag, long_tag_encoded, shortTagLen) == 0)
			{
				unsigned char short_tag_new[shortTagLen + 1];
				strncpy((char*)short_tag_new, long_tag_encoded, shortTagLen);
				short_tag_new[shortTagLen] = '\0';
				
				printf("Found new tag: %s -> %s\n", plain_tag, long_tag_encoded);
                
                if (s_num_tags != -1) {
                    
                    #pragma omp critical
                    {
						num_tags--;
					}
				}
				
				tags_found++;
			}
			
			//increment the suffix_rep by 1
			baseIncrementer(suffix_rep, alphanumLen, suffix_size);
			tags_checked++;
			index++;
		}
		
		#pragma omp barrier
		
		printf("Num Tags checked by thread %d: %llu\n", i, tags_checked);
	}
	
	printf("\n");
	printf("Total Num Tags Checked: %llu\n", tags_checked);
	printf("Total Num Tags Found: %llu\n", tags_found);
}