#include <stdio.h>
long sum_to(int n) {
    long total = 0;
    for (int i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}
int main() {
    printf("%ld\n", sum_to(1000000));
    return 0;
}
