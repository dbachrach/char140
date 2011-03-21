#include <stdlib.h>
#include <stdio.h>
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

static const char alphanum[] =
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz";

int main(int argc, char *argv[])
{	
	char *short_tag = argv[1];
	char *prefix = argv[2];
	int exploration_space_lower_bound = atoi(argv[3]);
	int exploration_space_upper_bound = atoi(argv[4]);
	int exploration_space_size = exploration_space_upper_bound - exploration_space_lower_bound;
	int num_tags = atoi(argv[5]);
	int threads = atoi(argv[6]);
	omp_set_num_threads(threads);
	
	int time_seed = time(NULL);
	
	
	#pragma omp parallel for default(shared)
	for (int thread_num = 0; thread_num < threads; thread_num++)
	{		
		int seed_num = time_seed + thread_num;
		
		printf("seed(%d): %d\n", thread_num, time_seed + thread_num);

		int n = strlen(short_tag);
		
		char plain_tag[exploration_space_size + 1];
		
		unsigned char long_tag[20];
		
		
		//
		// Byte accurate calculation of final buffer size
		//
		size_t long_tag_encoded_size =
				((20 / BINARY_UNIT_SIZE)
					+ ((20 % BINARY_UNIT_SIZE) ? 1 : 0))
						* BASE64_UNIT_SIZE;

		//
		// Include space for a terminating zero
		//
		long_tag_encoded_size += 1;
		
		char long_tag_encoded[long_tag_encoded_size];
		
		unsigned long long int tags_checked = 0;
		
		while(num_tags > 0)
		{
			// Generate random string
			int len = rand_r(&seed_num) % exploration_space_size + exploration_space_lower_bound;	
			for (int a = 0; a < len; a++) 
			{
		        plain_tag[a] = alphanum[rand_r(&seed_num) % (sizeof(alphanum) - 1)];
		    }
		    plain_tag[len] = '\0';

			//CC_SHA1(plain_tag, len, long_tag);
			SHA1(plain_tag, len, long_tag);

			NewBase64Encode(long_tag, 20, 0, NULL, long_tag_encoded);
			
			// Compares the input short tag to the long tag truncated to the length of the short tag
			if (strncmp(short_tag, long_tag_encoded, n) == 0)
			{
				unsigned char short_tag_new[n + 1];
				strncpy(short_tag_new, long_tag_encoded, n);
				short_tag_new[n] = '\0';
				
				printf("Found new tag: %s -> %s\n", plain_tag, short_tag_new);
				#pragma omp critical
				{
					num_tags--;
				}
			}
			tags_checked++;
		}
		
		printf("Tags Checked (%d): %llu\n", thread_num, tags_checked);
	}
}