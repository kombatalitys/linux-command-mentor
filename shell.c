#include <stdio.h>
#include <string.h>
#include <unistd.h>
int main(int argc, char *argv[]) {
if(argc < 2) {
printf("usage: %s <command>", argv[0]);
return 1;
}
char *command = argv[1];
if(strcmp(command, "help") == 0) {
printf("you typed help. in a real shell this is used to display the info of another command");
} else if(strcmp(command, "rm") == 0) {
printf("you typed rm. be careful with this one, since if you type rm -rf / you can destroy a system");
} else if(strcmp(command, "sudo") == 0) {
printf("you typed sudo. this is used for changing the priveleges of a command");
} else if(strcmp(command, "ls") == 0) {
printf("you typed ls. this is used for listing files or directories");
} else if(strcmp(command, "grep") == 0) {
printf("grep is used to search files. for example, you could use it to search if a file contains a specific word");
} else if(strcmp(command, "cat") == 0) {
printf("you typed cat. it is not an animal, it is a command that displays the contents of a file");
} else if(strcmp(command, "i am a complete beginner") == 0) {
printf("oh, a beginner? let us get you started");
execlp("firefox", "firefox", "https://wiki.archlinux.org", NULL);
} else if(strcmp(command, "i do not know what to type") == 0) {
printf("get the hell out of here");
}
}
// i was just tired of typing
