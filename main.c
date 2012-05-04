#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    for (;;) {
        char line_buffer[LINE_MAX];
        FILE *aps_file = popen("nmcli -t -e no -f bssid,signal dev wifi", "r");

        if (!aps_file) {
            fprintf(stderr, "Could not execute nmcli command\n");
            return EXIT_FAILURE;
        }

        while (fgets(line_buffer, LINE_MAX, aps_file)) {
            printf("%s", line_buffer);
        }

        pclose(aps_file);

        sleep(5);
    }

    return 0;
}
