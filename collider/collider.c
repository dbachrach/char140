#include <stdlib.h>
#include <stdio.h>
#include <math.h>
// #include <CommonCrypto/CommonDigest.h>
#include <omp.h>
#include <string.h>
#include <time.h>
#include <openssl/sha.h>

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
 *	Creates an array of size num_digits padded with zeros and fills in the digits of (num)output_base.
 *  A pointer to the array is assigned to result_buffer; 
 */
void baseConverter(int num, int output_base, int num_digits, int** result_buffer) {
	
	int* buffer = malloc(num_digits * sizeof(int));
	int M = num;
	int offset = 0;
	
	for(int i = 0; i < num_digits; i++)
		buffer[i] = 0;
	
	while (M >= output_base) {
		
		int temp = M % output_base;
		buffer[num_digits - offset - 1] = temp;
		M = M/output_base;
		offset++;
		
		if(offset >= num_digits) {
			
			printf("Entered number that exceeded number of digits allowable for num %d, digits %d", num, num_digits);
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
		
		if(num[i] = base - 1) {
			
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
int* getIterationChunks(int exploration_space_size, int num_threads) {
	
	int exploration_chunks = exploration_space_size	/ num_threads;
	int exploration_chunks_remainder = exploration_space_size % num_threads;
	int* iterationChunks = malloc(num_threads * sizeof(int));
	
	for( int i = 0; i < num_threads; i++ )
		iterationChunks[i] = exploration_chunks;
	
	int index = 0;
	while (exploration_chunks_remainder != 0 ) {
		
		iterationChunks[index % num_threads] += 1;
		index++;
		exploration_chunks_remainder--;
	}
	
	return iterationChunks;
}

static const char* alphanums = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

int main(int argc, char *argv[])
{	
	unsigned char *short_tag = argv[1];
	unsigned char *prefix = argv[2];
	int suffix_size = atoi(argv[3]);
	int num_tags = atoi(argv[4]);
	int threads = atoi(argv[5]);
	
	omp_set_num_threads(threads);
	
	int time_seed = time(NULL);
	int exploration_space_size = (int)pow(64, suffix_size) - 1;
	
	if (exploration_space_size < 0) {
		
		printf("Num bytes for suffix is too large. Exiting...");
		return 0;
	}
	
	//
	// Byte accurate calculation of final buffer size
	//
	size_t long_tag_encoded_size = ((20 / BINARY_UNIT_SIZE) + ((20 % BINARY_UNIT_SIZE) ? 1 : 0)) * BASE64_UNIT_SIZE;
	
	//
	// Include space for a terminating zero
	//
	long_tag_encoded_size += 1;
	
	srand(time_seed);
	int startPos = rand() % exploration_space_size;
	int* iterationChunks = getIterationChunks(exploration_space_size, threads);
	
	int shortTagLen = strlen(short_tag);
	int prefixLen = strlen(prefix);
	int alphanumLen = strlen(alphanums);
	unsigned long long tags_checked = 0;
	
	#pragma omp parallel for default(none) \
	private(short_tag, shortTagLen, prefix, prefixLen, suffix_size, long_tag_encoded_size, startPos, threads, iterationChunks, exploration_space_size, alphanums, alphanumLen) \
	shared(num_tags) \
	reduction(+: tags_checked)
	for (int i = 0; i < threads; i++)
	{		
		unsigned char plain_tag[prefixLen + suffix_size + 1];
		strncpy(plain_tag, prefix, prefixLen);
		
		unsigned char long_tag[20];
		
		char long_tag_encoded[long_tag_encoded_size];
		
		//compute the start position by advancing the start index by chunks
		int start = startPos;
		for (int j = 0; j < threads; j++) {
			
			if (j = i) {
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
		
		int index = 0;
		int numIterations = iterationChunks[i];
		
		while(num_tags > 0 && index < numIterations)
		{
			
			// Generate random string
			for (int a = 1; a <= suffix_size; a++) 
			{
		        plain_tag[prefixLen + a] = alphanums[suffix_rep[suffix_size - a]];
		    }
			
		    plain_tag[prefixLen + suffix_size + 1] = '\0';
			
			//CC_SHA1(plain_tag, len, long_tag);
			SHA1(plain_tag, prefixLen + suffix_size, long_tag);
			
			NewBase64Encode(long_tag, 20, 0, NULL, long_tag_encoded);
			
			// Compares the input short tag to the long tag truncated to the length of the short tag
			if (strncmp(short_tag, long_tag_encoded, shortTagLen) == 0)
			{
				unsigned char short_tag_new[shortTagLen + 1];
				strncpy(short_tag_new, long_tag_encoded, shortTagLen);
				short_tag_new[shortTagLen] = '\0';
				
				printf("Found new tag: %s -> %s\n", plain_tag, short_tag_new);
				#pragma omp critical
				{
					num_tags--;
				}
			}
			
			baseIncrementer(suffix_rep, alphanumLen, suffix_size);
			tags_checked++;
			index++;
		}
	}
	
	printf("Num Tags Checked: %llu\n", tags_checked);
}