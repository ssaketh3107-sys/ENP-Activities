#include <stdio.h>
#include <math.h>

#define RECESSIVE_THRESHOLD 0.5
#define DOMINANT_THRESHOLD  0.9
#define EPS 1e-6

int main(void) {
    double can_h, can_l;
    long bit_rate;
    printf("CAN_H voltage (V): ");
    scanf("%lf", &can_h);
    printf("CAN_L voltage (V): ");
    scanf("%lf", &can_l);
    printf("Bus bit rate (bps): ");
    scanf("%ld", &bit_rate);

    double vdiff = can_h - can_l;

    printf("\nCAN_H = %.2f V\nCAN_L = %.2f V\nVdiff = %.2f V\nBit rate = %ld bps\n",
           can_h, can_l, vdiff, bit_rate);

    printf("CAN BUS STATE : ");
    if (fabs(vdiff - RECESSIVE_THRESHOLD) < EPS)
        printf("BOUNDARY\n");
    else if (vdiff < RECESSIVE_THRESHOLD)
        printf("RECESSIVE\n");
    else if (vdiff > DOMINANT_THRESHOLD)
        printf("DOMINANT\n");
    else
        printf("INVALID / NOISE REGION\n");

    return 0;
}