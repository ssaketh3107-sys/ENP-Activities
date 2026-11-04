#include <stdio.h>

#define MAX_NODES 30

typedef struct {
    const char *name, *noise, *radiation, *use;
    int wires, max_noise;      /* max_noise: tolerable noise level in % */
    double len_factor;         /* derating on max bus length */
} Medium;

static const Medium M[] = {
    {"Single Wire",                "LOW",       "HIGH",     "Low-cost, short-range, non-critical", 1, 20, 0.5},
    {"Differential Twisted Pair",  "HIGH",      "LOW",      "General automotive / industrial",     2, 50, 1.0},
    {"Twisted Pair + Screen",      "VERY HIGH", "VERY LOW", "Harsh EMI environments",              2, 80, 1.0},
};

static double max_len(int kbps) {
    return kbps >= 1000 ? 40 : kbps >= 500 ? 100 : kbps >= 250 ? 250 : 500;
}

/* returns NULL if suitable, otherwise the reason it is not */
static const char *check(const Medium *m, int kbps, double len, int nodes,
                         int fault, int noise, int term) {
    if (fault)                          return fault == 1 ? "open-circuit fault" : "short-circuit fault";
    if (!term)                          return "termination absent";
    if (len > max_len(kbps) * m->len_factor) return "bus too long for bit rate";
    if (nodes > MAX_NODES)              return "too many nodes";
    if (noise > m->max_noise)           return "noise level too high";
    return NULL;
}

int main(void) {
    int sel, kbps, nodes, fault, noise, term;
    double len;

    printf("Medium (1=Single Wire, 2=Diff Pair, 3=Twisted+Screen): "); scanf("%d", &sel);
    printf("Bit rate (125/250/500/1000 kbps): ");                      scanf("%d", &kbps);
    printf("Bus length (m): ");                                        scanf("%lf", &len);
    printf("Number of nodes: ");                                       scanf("%d", &nodes);
    printf("Fault (0=None, 1=Open, 2=Short): ");                       scanf("%d", &fault);
    printf("Noise level (0-100 %%): ");                                scanf("%d", &noise);
    printf("Termination (0=Absent, 1=Present): ");                     scanf("%d", &term);

    if (sel < 1 || sel > 3) { printf("Invalid medium\n"); return 1; }
    const Medium *m = &M[sel - 1];
    const char *why = check(m, kbps, len, nodes, fault, noise, term);

    printf("\nCAN Medium      : %s\n", m->name);
    printf("Wires           : %d\n", m->wires);
    printf("Noise Rejection : %s\n", m->noise);
    printf("Radiation       : %s\n", m->radiation);
    printf("Bit Rate        : %d kbps\n", kbps);
    printf("Bus Length      : %.0f m\n", len);
    printf("Nodes           : %d\n", nodes);
    printf("Fault Effect    : %s\n", fault == 0 ? "None" : fault == 1 ? "Open - signal lost" : "Short - bus stuck");
    printf("Termination     : %s\n", term ? "OK" : "MISSING");
    printf("Bus Status      : %s%s%s\n", why ? "NOT SUITABLE (" : "SUITABLE", why ? why : "", why ? ")" : "");
    printf("Recommended Use : %s\n", m->use);

    /* Extension: compare against all media */
    printf("\n--- Comparison ---\n");
    for (int i = 0; i < 3; i++) {
        const char *r = check(&M[i], kbps, len, nodes, fault, noise, term);
        printf("%-27s noise:%-9s rad:%-8s -> %s%s\n", M[i].name, M[i].noise,
               M[i].radiation, r ? "NOT SUITABLE: " : "SUITABLE", r ? r : "");
    }
    return 0;
}
