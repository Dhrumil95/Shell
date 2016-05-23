#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <signal.h>
#include <ctype.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h> // for open() function

/* Forward Declaration of functions */
bool check_empty_string(char *character); // Checks if the Input is empty.
/* conv_tokens:  Breaks the line into segments. Tokens are created at every (space) " ". i.e. Parse the line into tokens */
void conv_tokens(char *commandlineInput, char** token, int *total_token); 
void sigint_msg(); // Ctrl-C signal handler
void startProcess(char **tokenArr, int total_tokens); // Starts the exec process. Handles I/O redirection too.
void sigtstp_msg(); // Ctrl-Z signal handler

int main(int argc, char *argv[]) {
	
	/* 
	 * Detects signal
	 * Prints error if signal_error occured
	 */
	if ( signal(SIGINT, sigint_msg) == SIG_ERR )   perror("SIGINT signal err");
	if ( signal(SIGTSTP, sigtstp_msg) == SIG_ERR ) perror("SIGTSTP signal err");

	/* loops until user exters "exit" */
	while(true) { 
		printf("CS361 > "); // prompt
		
		char commandlineInput[256]; //assuming max args will be 256
		fgets(commandlineInput, 256, stdin); // Store the input from stdin to commandlineInput char array 
		
		/*
		 * check_empty_string : Checks if the string is empty. Prevents causing seg fault. Returns true or false
		 * If empty string was entered, it skips the iteration and starts all over again.
		 */
		if (check_empty_string(commandlineInput)) continue;
		
		int total_tokens = 0;
		/*
		 * conv_tokens: breaks the line into strings at every " " (space) and stores it in tokenArr dynamic array as tokens
		 * The function dies not return anything.
		 * The function also stores the number of tokens in total_token var via pointer.
		 * Sets the last element as NULL so execvp knows when to stop.
		 */
		char **tokenArr = malloc(sizeof(tokenArr) * 256);
		conv_tokens(commandlineInput, tokenArr, &total_tokens);		
		tokenArr[total_tokens] = NULL;
		
		/*
		 * startProcess: The process of executing the commads starts here.
		 * The function does not return anything
		 */
		startProcess(tokenArr, total_tokens);
	}
	return 0;
}

void conv_tokens(char *commandlineInput, char** token, int *total_token) {
	int arrIndex = 0; // keeping tract of index in dynamic array
	char *currtoken; // Goes through each string. Used for storing current token
	
	/* The loop stores the string via strtok at every " " (space) in currtoken 
	 * stores the current token(currtoken) in alloc_token array. arrIndex increases through each interation 
	 */
	for (currtoken = strtok(commandlineInput, " \n"); currtoken != NULL; currtoken = strtok(NULL, " \n"), arrIndex++ )
		token[arrIndex] = currtoken;
	
	*total_token = arrIndex; // Number of total tokens are passed into the total_token var
}

/* Used to store the tokens before the I/O redirection symbol */
char** copy_tokens(int num_token, char **tokenArr ) {
	char **redirected_tokens = malloc(sizeof(redirected_tokens) * num_token); // allocate memory according according to the number of tokens 
	
	/* This loop stores the tokens to a new array */
	int arrIndex = 0;
	while ( arrIndex < num_token ) {
		redirected_tokens[arrIndex] = tokenArr[arrIndex];
		arrIndex++;
	}
	redirected_tokens[num_token] = NULL; // set last element to NULL
	
	return redirected_tokens; // return the array
}

void startProcess(char **tokenArr, int total_tokens)
{
	if ( !strcmp(tokenArr[0], "exit") ) exit(0); // If first command is "exit". The program exits with 0

	pid_t pid; // Get Process ID
	bool stdin_flag = false, stdout_flag = false; // Needed for dup2 function and copy_tokens function.
	int status, fd = 0; // needed for wait() and open()
	
	pid = fork();
	if (pid >= 0) /* fork succeeded */
	{
	  if (pid == 0)
	  {
		/* This loop basically goes through each token and checks for any I/O redirection was entered */
		int num_token = 0;
		while ( num_token < total_tokens - 1 ) {
			const char *file = tokenArr[num_token + 1];
			if ( !strcmp(tokenArr[num_token], ">") ) {
				fd = open(file, O_RDWR|O_TRUNC|O_CREAT, 0666); stdout_flag = true; 
				break;
			} else if ( !strcmp(tokenArr[num_token], ">>") ) {
				fd = open(file, O_RDWR|O_APPEND|O_CREAT , 0666); stdout_flag = true;
				break; 
			} else if ( !strcmp(tokenArr[num_token], "<") ) {
				fd = open(file, O_RDWR , 0666); stdin_flag = true;
				break;
			}
			num_token++; // Stores the number of tokens before redirection symbol is used.
		}
		
		/*
		 * Removes anything after the I/O redirection symbol
		 * Also removes the file(name) token and redirection token
		 * store the tokens in new dynamic array : redirected_tokens 
		 */
		char **redirected_tokens = copy_tokens( ( stdout_flag || stdin_flag ) ? num_token : num_token + 1 , tokenArr);
		
		if ( fd == -1 ) perror("\nCan't Open File\n"); // Open() failed
		
		if ( stdout_flag ) dup2(fd, 1); // for stdout
		else 		       dup2(fd, 0); // for stdin
		close(fd);						// close
		
		// passes the new tokens into execvp
		execvp(redirected_tokens[0], redirected_tokens);
		exit(EXIT_FAILURE);
		
		} else /* parent process */ {
			wait(&status);
			if (WIFEXITED(status)) printf("pid:%d status:%d (exited normally)\n", pid, WEXITSTATUS(status));
	        else if (WIFSIGNALED(status)) printf("pid:%d status:%d (uncaught signal)\n", pid, WTERMSIG(status));
		}
	} else /* failure */ {
		perror("fork failure");
		exit(0);
	}
}

/* Ctrl-C Signal Handler */
void sigint_msg() {
	FILE *fp = stdout;
	
	printf("\ncatch sigint");
	printf("\nCS361 > ");

	fflush(fp);
}

/* Ctrl-Z Signal Handler */
void sigtstp_msg() { 
	FILE *fp = stdout;
	
	printf("\ncatch sigtstp");
	printf("\nCS361 > ");

	fflush(fp);
}

/* Check of the string is empty */
bool check_empty_string(char *character) {
	
	for (; *character != '\0'; character++) 
		if ( !isspace(*character) ) return false;
	
	return true;
}

