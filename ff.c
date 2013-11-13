#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <assert.h>

#define FF_SIZE          8
#define FF_PRIM_POLY     0x1b
#define FF_GENERATOR     0x03
#define FF_ELEM_NUM      (2<<(FF_SIZE-1))
#define FF_ELEM_MASK     (FF_ELEM_NUM-1)

/******************************************************************************/

uint8_t ff8_exp_table[FF_ELEM_NUM];
uint8_t ff8_log_table[FF_ELEM_NUM];
uint8_t ff8_sqrt_table[FF_ELEM_NUM];
uint8_t ff8_mul_table[FF_ELEM_NUM][FF_ELEM_NUM];
uint8_t ff8_div_table[FF_ELEM_NUM][FF_ELEM_NUM];

/******************************************************************************/

uint8_t ff8_slow_mul(uint8_t a, uint8_t b) {
    uint8_t p;
    int i;

    p = 0;
    for (i = 0; i < FF_SIZE; i++) {
        if (b & 0x1)
            p ^= a;
        if (a & (1 << (FF_SIZE-1))) {
            a <<= 1;
            a &= FF_ELEM_MASK;
            a ^= FF_PRIM_POLY;
        } else {
            a <<= 1;
            a &= FF_ELEM_MASK;
        }
        b >>= 1;
    }

    return p;
}

uint8_t ff8_slow_sqrt(uint8_t x) {
    int i;

    for (i = 0; i < FF_ELEM_NUM; i++) {
        if (ff8_slow_mul(i, i) == x)
            return i;
    }

    fprintf(stderr, "error! no sqrt for %d in this finite field!\n", x);
    assert(0);

    return 0;
}

uint8_t ff8_exp_mul(uint8_t a, uint8_t b) {
    uint8_t exp_index;

    if (a == 0 || b == 0)
        return 0;

    /* a * b = exp(log(a)) * exp(log(b)) = exp(log(a) + log(b)) */
    exp_index = (ff8_log_table[a] + ff8_log_table[b]) % FF_ELEM_MASK;
    return ff8_exp_table[exp_index];
}

uint8_t ff8_exp_div(uint8_t a, uint8_t b) {
    uint8_t b_inverse;
    if (b == 0) {
        fprintf(stderr, "error! division by zero!\n");
        assert(0);
    }

    /* a / b = a * (1/b) */
    b_inverse = ff8_exp_table[FF_ELEM_NUM - 1 - ff8_log_table[b]];
    return ff8_exp_mul(a, b_inverse);
}

/******************************************************************************/

void ff8_precompute(void) {
    int i, j;

    /* Precompute exponent and log tables */
    ff8_exp_table[0] = 0x1;
    ff8_log_table[0] = 0x0;
    for (i = 1; i < FF_ELEM_NUM; i++) {
        ff8_exp_table[i] = ff8_slow_mul(ff8_exp_table[i-1], FF_GENERATOR);
        ff8_log_table[ff8_exp_table[i]] = i;
    }

    /* Precompute sqrt table */
    for (i = 0; i < FF_ELEM_NUM; i++)
        ff8_sqrt_table[i] = ff8_slow_sqrt(i);

    /* Precompute multiplication table */
    for (i = 0; i < FF_ELEM_NUM; i++)
        for (j = 0; j < FF_ELEM_NUM; j++)
            ff8_mul_table[i][j] = ff8_exp_mul(i, j);

    /* Precompute division table */
    for (i = 0; i < FF_ELEM_NUM; i++)
        for (j = 1; j < FF_ELEM_NUM; j++)
            ff8_div_table[i][j] = ff8_exp_div(i, j);
}

/******************************************************************************/

uint8_t ff8_add(uint8_t a, uint8_t b) {
    return a ^ b;
}

uint8_t ff8_sub(uint8_t a, uint8_t b) {
    return a ^ b;
}

uint8_t ff8_mul(uint8_t a, uint8_t b) {
    return ff8_mul_table[a][b];
}

uint8_t ff8_div(uint8_t a, uint8_t b) {
    if (b == 0) {
        fprintf(stderr, "error! division by zero!\n");
        assert(0);
    }
    return ff8_div_table[a][b];
}

uint8_t ff8_sqrt(uint8_t a) {
    return ff8_sqrt_table[a];
}

/******************************************************************************/

void ff8_test(void) {
    int a, b;

    ff8_precompute();

    for (a = 0; a < FF_ELEM_NUM; a++) {
        for (b = 0; b < FF_ELEM_NUM; b++) {
            /* assert 0 + a = a + 0 = a */
            assert(ff8_add(0, a) == a);
            /* assert a + b = b + a */
            assert(ff8_add(a, b) == ff8_add(b, a));
            /* assert a - b + b = a */
            assert(ff8_add(ff8_sub(a, b), b) == a);

            /* assert a * b = b * a */
            assert(ff8_mul(a, b) == ff8_mul(b, a));
            /* assert (a * b) / b = a */
            if (b != 0)
                assert(ff8_div(ff8_mul(a, b), b) == a);
            /* assert (a / b) * b = a */
            if (b != 0)
                assert(ff8_mul(ff8_div(a, b), b) == a);

            /* assert sqrt(a * a) == a */
            assert(ff8_sqrt(ff8_mul(a, a)) == a);

            /* assert sqrt(a)*sqrt(a) == a */
            assert(ff8_mul(ff8_sqrt(a), ff8_sqrt(a)) == a);
        }
    }
}

/******************************************************************************/

#define MAX_ROWS    2048
#define MAX_COLS    2048

/* Matrix A is an array of pointers to rows, so we can do fast row swaps */
uint8_t *matrix[MAX_ROWS];
int matrix_rows, matrix_cols;

/* matrix[i] <-> matrix[j] */
void matrix_row_swap(int i, int j) {
    uint8_t *temp;
    temp = matrix[i];
    matrix[i] = matrix[j];
    matrix[j] = temp;
}

/* matrix[i] = matrix[i] ./ c */
void matrix_row_div(int i, uint8_t c) {
    int j;
    for (j = 0; j < matrix_cols; j++)
        matrix[i][j] = ff8_div(matrix[i][j], c);
}

/* matrix[i] = matrix[i] .* c */
void matrix_row_mul(int i, uint8_t c) {
    int j;
    for (j = 0; j < matrix_cols; j++)
        matrix[i][j] = ff8_mul(matrix[i][j], c);
}

/* matrix[i] = matrix[i] - (matrix[j] .* c) */
void matrix_row_submul(int i, int j, uint8_t c) {
    int k;
    for (k = 0; k < matrix_cols; k++)
        matrix[i][k] = ff8_sub(matrix[i][k], ff8_mul(matrix[j][k], c));
}

/* Find solved index of matrix[r] row */
int matrix_solved_index(int r) {
    int i, solved_index = -1;

    for (i = 0; i < matrix_cols; i++) {
        if (matrix[r][i] != 0) {
            if (solved_index != -1)
                return -1;
            solved_index = i;
        }
    }

    return solved_index;
}

void matrix_debug_dump(void) {
    int i, j;

    for (j = 0; j < matrix_rows; j++) {
        for (i = 0; i < matrix_cols; i++) {
            printf("%d ", matrix[j][i]);
        }
        printf("\n");
    }
}

bool matrix_debug_compare(uint8_t *vector) {
    int i, j;

    for (j = 0; j < matrix_rows; j++) {
        for (i = 0; i < matrix_cols; i++) {
            if (vector[j*matrix_cols + i] != matrix[j][i])
                return false;
        }
    }

    return true;
}

void matrix_rref(void) {
    int i, j, k, pi;
    bool done = false;

    /* Pivot index */
    pi = 0;

    for (j = 0; j < matrix_rows; j++) {
        /* While we do not have a pivot for this row */
        while (matrix[j][pi] == 0) {
            /* Find a row below to swap with for a pivot at pi */
            for (k = j+1; k < matrix_rows; k++) {
                if (matrix[k][pi] != 0) {
                    matrix_row_swap(j, k);
                    break;
                }
            }

            /* Increment pivot index, if we could not find a row to swap with */
            if (matrix[j][pi] == 0)
                pi += 1;

            /* If there is no pivots left, we're done reducing */
            if (pi == matrix_cols) {
                done = true;
                break;
            }
        }

        if (done)
            break;

        /* Divide through to have a pivot of 1 */
        matrix_row_div(j, matrix[j][pi]);

        /* Eliminate above and below */
        for (k = 0; k < matrix_rows; k++) {
            if (k != j && matrix[k][pi] != 0)
                matrix_row_submul(k, j, matrix[k][pi]);
        }

        /* Move onto the next pivot */
        pi += 1;

        /* If there no pivots left, we're done, reducing */
        if (pi == matrix_cols)
            break;
    }
}

/******************************************************************************/

void matrix_util_clear(uint16_t *solved_indices, uint8_t *flat_matrix, int m, int n) {
    assert(m <= MAX_ROWS);
    assert(n <= MAX_COLS);

    memset(solved_indices, 0, sizeof(uint16_t)*n);
    memset(flat_matrix, 0, sizeof(uint8_t)*m*n);
}

int matrix_solve(uint16_t *solved_indices, uint8_t *flat_matrix, int m, int n) {
    int i, j, num_solved;

    matrix_rows = m;
    matrix_cols = n;

    assert(matrix_rows <= MAX_ROWS);
    assert(matrix_cols <= MAX_COLS);

    /* Load the matrix */
    for (j = 0; j < matrix_rows; j++)
        matrix[j] = &flat_matrix[j*n];

    /* Do the rref */
    matrix_rref();

    /* Find the count and indices of solved columns */
    num_solved = 0;
    for (j = 0; j < matrix_rows; j++) {
        if ((i = matrix_solved_index(j)) != -1)
            solved_indices[num_solved++] = i;
    }

    /* Return count of solved columns */
    return num_solved;
}

int matrix_test_solve(uint16_t *solved, uint8_t *flat_matrix, int m, int n) {
    int i, j;

    printf("got solve for %d by %d\n", m, n);

    printf("matrix dump\n");
    for (j = 0; j < m; j++) {
        for (i = 0; i < n; i++)
            printf("%02x,", flat_matrix[j*n + i]);
        printf("\n");
    }

    solved[0] = 5;
    solved[1] = 2;
    solved[2] = 1;

    return 3;
}

/******************************************************************************/

#define MATRIX_STATIC_ROW(...) ((uint8_t *)(&(uint8_t []){ __VA_ARGS__ }))

void matrix_test(void) {
    int i, j, k;

    matrix_rows = 4;
    matrix_cols = 5;

    matrix[0] = MATRIX_STATIC_ROW(24, 21, 118, 193, 137);
    matrix[1] = MATRIX_STATIC_ROW(76, 92, 70, 155, 167);
    matrix[2] = MATRIX_STATIC_ROW(226, 249, 37, 53, 147);
    matrix[3] = MATRIX_STATIC_ROW(120, 228, 148, 34, 32);

    /* Test row swap */
    matrix_row_swap(0, 2);
    assert(matrix[0][0] == 226);
    assert(matrix[0][1] == 249);
    assert(matrix[0][2] == 37);
    assert(matrix[0][3] == 53);
    assert(matrix[0][4] == 147);
    assert(matrix[2][0] == 24);
    assert(matrix[2][1] == 21);
    assert(matrix[2][2] == 118);
    assert(matrix[2][3] == 193);
    assert(matrix[2][4] == 137);

    /* Test row multiplication */
    matrix_row_mul(1, 4);
    assert(matrix[1][0] == 43);
    assert(matrix[1][1] == 107);
    assert(matrix[1][2] == 3);
    assert(matrix[1][3] == 90);
    assert(matrix[1][4] == 170);

    /* Test row division */
    matrix_row_div(1, 4);
    assert(matrix[1][0] == 76);
    assert(matrix[1][1] == 92);
    assert(matrix[1][2] == 70);
    assert(matrix[1][3] == 155);
    assert(matrix[1][4] == 167);

    /* Test row subtraction of another row multiple */
    matrix_row_submul(3, 0, 5);
    assert(matrix[3][0] == 63);
    assert(matrix[3][1] == 212);
    assert(matrix[3][2] == 37);
    assert(matrix[3][3] == 195);
    assert(matrix[3][4] == 201);

    /* Test rref */
    {
        uint8_t vector[] = {1, 0, 0, 0, 226, 0, 1, 0, 0, 190, 0, 0, 1, 0, 234, 0, 0, 0, 1, 37};
        matrix_rref();
        assert(matrix_debug_compare(vector));
    }

    matrix_rows = 3;
    matrix_cols = 3;

    {
        uint8_t vector[] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
        matrix[0] = MATRIX_STATIC_ROW(0, 0, 0);
        matrix[1] = MATRIX_STATIC_ROW(0, 0, 0);
        matrix[2] = MATRIX_STATIC_ROW(0, 0, 0);
        matrix_rref();
        assert(matrix_debug_compare(vector));
        assert(matrix_solved_index(0) == -1);
        assert(matrix_solved_index(1) == -1);
        assert(matrix_solved_index(2) == -1);
    }

    {
        uint8_t vector[] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
        matrix[0] = MATRIX_STATIC_ROW(1, 0, 0);
        matrix[1] = MATRIX_STATIC_ROW(0, 1, 0);
        matrix[2] = MATRIX_STATIC_ROW(0, 0, 1);
        matrix_rref();
        assert(matrix_debug_compare(vector));
        assert(matrix_solved_index(0) == 0);
        assert(matrix_solved_index(1) == 1);
        assert(matrix_solved_index(2) == 2);
    }

    {
        uint8_t vector[] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
        matrix[0] = MATRIX_STATIC_ROW(5, 0, 0);
        matrix[1] = MATRIX_STATIC_ROW(0, 3, 0);
        matrix[2] = MATRIX_STATIC_ROW(0, 0, 2);
        matrix_rref();
        assert(matrix_debug_compare(vector));
        assert(matrix_solved_index(0) == 0);
        assert(matrix_solved_index(1) == 1);
        assert(matrix_solved_index(2) == 2);
    }

    {
        uint8_t vector[] = {1, 0, 0, 0, 0, 0, 0, 0, 0};
        matrix[0] = MATRIX_STATIC_ROW(5, 0, 0);
        matrix[1] = MATRIX_STATIC_ROW(2, 0, 0);
        matrix[2] = MATRIX_STATIC_ROW(9, 0, 0);
        matrix_rref();
        assert(matrix_debug_compare(vector));
        assert(matrix_solved_index(0) == 0);
        assert(matrix_solved_index(1) == -1);
        assert(matrix_solved_index(2) == -1);
    }

    {
        uint8_t vector[] = {1, 0, 0, 0, 0, 1, 0, 0, 0};
        matrix[0] = MATRIX_STATIC_ROW(5, 0, 0);
        matrix[1] = MATRIX_STATIC_ROW(5, 0, 0);
        matrix[2] = MATRIX_STATIC_ROW(0, 0, 2);
        matrix_rref();
        assert(matrix_debug_compare(vector));
        assert(matrix_solved_index(0) == 0);
        assert(matrix_solved_index(1) == 2);
        assert(matrix_solved_index(2) == -1);
    }

    {
        uint8_t vector[] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
        matrix[0] = MATRIX_STATIC_ROW(1, 2, 3);
        matrix[1] = MATRIX_STATIC_ROW(4, 4, 7);
        matrix[2] = MATRIX_STATIC_ROW(3, 6, 10);
        matrix_rref();
        assert(matrix_debug_compare(vector));
        assert(matrix_solved_index(0) == 0);
        assert(matrix_solved_index(1) == 1);
        assert(matrix_solved_index(2) == 2);
    }

    matrix_cols = 5;
    matrix_rows = 2;

    {
        uint8_t vector[] = {1, 101, 0, 0, 0, 0, 0, 1, 232, 0};
        matrix[0] = MATRIX_STATIC_ROW(23, 42, 0, 0, 0);
        matrix[1] = MATRIX_STATIC_ROW(0, 0, 59, 36, 0);
        matrix_rref();
        assert(matrix_debug_compare(vector));
        assert(matrix_solved_index(0) == -1);
        assert(matrix_solved_index(1) == -1);
    }

    /* Big rref */
    uint8_t row_pool[256][256];
    for (k = 0; k < 50; k++) {
        matrix_rows = sizeof(row_pool)/sizeof(row_pool[0]);
        matrix_cols = sizeof(row_pool[0])/sizeof(row_pool[0][0]);
        for (j = 0; j < matrix_rows; j++) {
            for (i = 0; i < matrix_cols; i++)
                row_pool[j][i] = rand() % FF_ELEM_NUM;
            matrix[j] = (uint8_t *)&row_pool[j];
        }
        matrix_rref();
    }

    /* Matrix solve interface */
    {
        uint8_t vector[] = {1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0};
        uint8_t flat_matrix[] = {1, 2, 3, 0, 4, 4, 7, 0, 3, 6, 10, 0};
        uint16_t solved[5];
        assert(matrix_solve(solved, vector, 3, 4) == 3);
        assert(matrix_debug_compare(vector));
    }
}

int main(void) {
    ff8_test();
    matrix_test();
    return 0;
}

